import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

import review  # noqa: E402

BLOCKER = (
    "Why this blocks:\nToken is logged.\n\n"
    "Required change:\nDo not log it.\n\n"
    "Verification:\nUnit test asserts log output omits the token."
)


def sh(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class Repo:
    """A throwaway git repo with main + a feature commit."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        sh(self.path, "init", "-q", "-b", "main")
        sh(self.path, "config", "user.email", "t@example.com")
        sh(self.path, "config", "user.name", "t")
        (self.path / "src").mkdir()
        (self.path / "src" / "auth.py").write_text("def login(u):\n    return u\n")
        (self.path / "README.md").write_text("# demo\n")
        sh(self.path, "add", "-A")
        sh(self.path, "commit", "-qm", "base")
        sh(self.path, "checkout", "-qb", "feature")
        (self.path / "src" / "auth.py").write_text(
            "def login(u, token):\n    print(token)\n    return u\n"
        )
        sh(self.path, "commit", "-qam", "feature")

    def commit(self, rel, text, msg="more"):
        (self.path / rel).write_text(text)
        sh(self.path, "add", "-A")
        sh(self.path, "commit", "-qm", msg)

    def run(self, *argv):
        with self._capture() as out:
            try:
                review.main(list(argv))
            except SystemExit as exc:
                code = exc.code
        return code, json.loads(out.getvalue())

    @staticmethod
    def _capture():
        import contextlib
        import io

        buf = io.StringIO()

        @contextlib.contextmanager
        def cm():
            with contextlib.redirect_stdout(buf):
                yield buf

        return cm()

    def close(self):
        self.tmp.cleanup()


def lens_result(head, lens, findings=None, disposition=None):
    findings = findings or []
    return {
        "kind": review.LENS_KIND,
        "lens": lens,
        "reviewed_head": head,
        "coverage": "complete",
        "disposition": disposition or ("findings" if findings else "pass"),
        "findings": findings,
        "limitations": [],
    }


def blocker(lens, line=2, supporting=None, rid="security:src/auth.py:2:token-logged"):
    return {
        "root_cause_id": rid,
        "origin": "semantic",
        "severity": "important",
        "path": "src/auth.py",
        "side": "RIGHT",
        "line": line,
        "summary": BLOCKER,
        "counter_search": "No redaction layer wraps print().",
        "supporting_lenses": supporting or [lens],
    }


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        code, out = self.repo.run("freeze", "--repo", str(self.repo.path), "--base", "main")
        self.assertEqual(code, 0, out)
        self.dir = Path(out["dir"])
        self.head = out["head"]
        self.ctx = json.loads((self.dir / "context.json").read_text())

    def tearDown(self):
        self.repo.close()

    def write(self, name, obj):
        p = self.dir / name
        p.write_text(json.dumps(obj))
        return str(p)

    def test_pr_text_saved_before_first_freeze_does_not_dirty_tree(self):
        fresh = Repo()
        try:
            (fresh.path / ".km-review").mkdir()
            (fresh.path / ".km-review" / "pr.json").write_text('{"title": "t", "body": "b"}')
            code, out = fresh.run("freeze", "--repo", str(fresh.path), "--base", "main",
                                  "--pr-text", str(fresh.path / ".km-review" / "pr.json"))
            self.assertEqual(code, 0, out)
        finally:
            fresh.close()

    def test_freeze_excludes_state_dir_and_rejects_dirty_tree(self):
        self.assertEqual(review.worktree_dirty(self.repo.path), [])
        (self.repo.path / "scratch.txt").write_text("x")
        code, out = self.repo.run("freeze", "--repo", str(self.repo.path), "--base", "main")
        self.assertEqual(code, 2)
        self.assertIn("not clean", out["error"])

    def test_auth_path_triggers_security_lens_and_panel_term(self):
        code, sel = self.repo.run("select", "--dir", str(self.dir))
        self.assertIn("security", sel["minimum_lenses"])
        self.assertIn("behavioral-evidence", sel["minimum_lenses"])
        self.assertEqual(sel["depth"], "panel")  # "auth" is a panel term

    def test_invalid_panel_plan_falls_back_to_full_roster(self):
        self.repo.run("select", "--dir", str(self.dir))
        bad = self.write("selector-plan.json", {"kind": review.PLAN_KIND, "head": self.head,
                                                 "lenses": [{"id": "security", "rationale": "x", "files": []}]})
        code, plan = self.repo.run("validate-plan", "--dir", str(self.dir), "--plan", bad)
        self.assertTrue(plan["fallback"])
        self.assertEqual(len(plan["parallel"]), 8)

    def test_valid_panel_plan_is_used(self):
        self.repo.run("select", "--dir", str(self.dir))
        good = self.write("selector-plan.json", {"kind": review.PLAN_KIND, "head": self.head, "lenses": [
            {"id": "security", "rationale": "token handling in login", "files": ["src/auth.py"]},
            {"id": "correctness", "rationale": "signature change", "files": ["src/auth.py"]},
            {"id": "behavioral-evidence", "rationale": "tests for login", "files": ["src/auth.py"]},
            {"id": "generalist", "rationale": "synthesis", "files": ["src/auth.py"]},
        ]})
        code, plan = self.repo.run("validate-plan", "--dir", str(self.dir), "--plan", good)
        self.assertFalse(plan["fallback"], plan)
        self.assertEqual(plan["parallel"], ["security", "correctness", "behavioral-evidence"])

    def _finalize_with(self, lenses, synthesis_findings):
        self.repo.run("select", "--dir", str(self.dir))
        self.repo.run("validate-plan", "--dir", str(self.dir))  # panel → fallback full roster
        plan = json.loads((self.dir / "plan.json").read_text())
        files = []
        for lid in [e["id"] for e in plan["lenses"] if e["id"] != "generalist"]:
            files.append(self.write(f"lens-{lid}.json", lenses.get(lid, lens_result(self.head, lid))))
        synth = self.write("synthesis.json", {
            "kind": review.SYNTH_KIND, "reviewed_head": self.head, "coverage": "complete",
            "consolidated_findings": synthesis_findings, "resolutions": [], "limitations": [],
        })
        return self.repo.run("finalize", "--dir", str(self.dir), "--lens", *files, "--synthesis", synth)

    def test_confirmed_blocker_is_not_ready(self):
        lenses = {"security": lens_result(self.head, "security", [blocker("security")])}
        code, out = self._finalize_with(lenses, [blocker("security", supporting=["security", "generalist"])])
        self.assertEqual(code, 1)
        self.assertEqual((out["status"], out["decision"], out["blockers"]), ("complete", "not_ready", 1))
        self.assertIn("Required changes (1)", (self.dir / "report.md").read_text())

    def test_single_confirmation_is_downgraded(self):
        lenses = {"security": lens_result(self.head, "security", [blocker("security")])}
        # generalist claims "operations" support, but operations never reported it.
        code, out = self._finalize_with(lenses, [blocker("security", supporting=["security", "operations"])])
        self.assertEqual((out["decision"], out["blockers"], out["downgrades"]), ("ready", 0, 1))

    def test_merged_raw_ids_count_as_confirmation(self):
        lenses = {
            "security": lens_result(self.head, "security", [blocker("security")]),
            "correctness": lens_result(self.head, "correctness", [
                blocker("correctness", rid="correctness:src/auth.py:2:prints-token")]),
        }
        merged = blocker("security", supporting=["security", "correctness"])
        merged["merged_from"] = ["correctness:src/auth.py:2:prints-token"]
        code, out = self._finalize_with(lenses, [merged])
        self.assertEqual((out["blockers"], out["downgrades"]), (1, 0))

    def test_blocker_on_unchanged_line_is_downgraded(self):
        lenses = {"security": lens_result(self.head, "security", [blocker("security", line=3)])}
        code, out = self._finalize_with(lenses, [blocker("security", line=3, supporting=["security", "generalist"])])
        agg = json.loads((self.dir / "aggregate.json").read_text())
        self.assertEqual(out["blockers"], 0)
        self.assertIn("not a changed line", agg["downgrades"][0]["reason"])

    def test_missing_lens_is_incomplete_not_pass(self):
        self.repo.run("select", "--dir", str(self.dir))
        self.repo.run("validate-plan", "--dir", str(self.dir))
        synth = self.write("synthesis.json", {
            "kind": review.SYNTH_KIND, "reviewed_head": self.head, "coverage": "complete",
            "consolidated_findings": [], "resolutions": [], "limitations": [],
        })
        code, out = self.repo.run("finalize", "--dir", str(self.dir), "--synthesis", synth)
        self.assertEqual((out["status"], out["decision"]), ("incomplete", "not_ready"))

    def test_clean_review_is_ready_and_head_move_is_stale(self):
        code, out = self._finalize_with({}, [])
        self.assertEqual((code, out["status"], out["decision"]), (0, "complete", "ready"))
        self.repo.commit("src/other.py", "x = 1\n")
        code, out = self.repo.run(
            "finalize", "--dir", str(self.dir),
            "--lens", *map(str, self.dir.glob("lens-*.json")),
            "--synthesis", str(self.dir / "synthesis.json"))
        self.assertEqual((out["status"], out["decision"]), ("stale", "not_ready"))

    def test_lens_validation_rejects_wrong_head_and_bad_summary(self):
        self.repo.run("select", "--dir", str(self.dir))
        self.repo.run("validate-plan", "--dir", str(self.dir))
        bad = blocker("security")
        bad["summary"] = "it is bad"
        res = lens_result("0" * 40, "security", [bad])
        code, out = self.repo.run("validate-lens", "--dir", str(self.dir), self.write("lens-security.json", res))
        errs = next(iter(out["results"].values()))["errors"]
        self.assertEqual(code, 1)
        self.assertTrue(any("reviewed_head" in e for e in errs))
        self.assertTrue(any("Why this blocks" in e for e in errs))

    def test_follow_up_requires_advanced_descendant_head(self):
        self._finalize_with({}, [])
        prior = str(self.dir / "aggregate.json")
        code, out = self.repo.run("freeze", "--repo", str(self.repo.path), "--base", "main", "--prior", prior)
        self.assertIn("not advanced", out["error"])
        self.repo.commit("src/auth.py", "def login(u, token):\n    return u\n", "fix")
        code, out = self.repo.run("freeze", "--repo", str(self.repo.path), "--base", "main", "--prior", prior)
        self.assertEqual((code, out["mode"]), (0, "follow-up"))


class SelectionTests(unittest.TestCase):
    def ctx(self, *paths, status="M"):
        return {"head": "a" * 40, "digest": "d", "files": [{"status": status, "path": p} for p in paths]}

    def select(self, ctx, requested=None):
        return review.compute_selection(ctx, review.load_json(SKILL_DIR / "selection-policy.json"),
                                        review.manifest(), requested)

    def test_docs_only_is_focused_with_docs_lens(self):
        sel = self.select(self.ctx("docs/guide.md"))
        self.assertEqual(sel["depth"], "focused")
        self.assertEqual(sel["minimum_lenses"], ["docs-and-claims", "generalist"])

    def test_plain_code_is_focused(self):
        sel = self.select(self.ctx("src/widgets/button.tsx"))
        self.assertEqual(sel["depth"], "focused")
        self.assertEqual(sel["minimum_lenses"], ["correctness", "behavioral-evidence", "generalist"])

    def test_sensitive_doc_name_does_not_force_panel(self):
        sel = self.select(self.ctx("docs/auth-flow.md"))
        self.assertEqual(sel["depth"], "focused")
        self.assertIn("security", sel["minimum_lenses"])  # lens trigger still applies

    def test_requested_panel_adds_correctness(self):
        sel = self.select(self.ctx("src/widgets/button.tsx"), "panel")
        self.assertEqual(sel["depth"], "panel")
        self.assertIn("correctness", sel["minimum_lenses"])

    def test_workflow_path_is_panel_with_operations(self):
        sel = self.select(self.ctx(".github/workflows/ci.yml"))
        self.assertEqual(sel["depth"], "panel")
        self.assertIn("operations", sel["minimum_lenses"])


class SuggestionPrefixTests(unittest.TestCase):
    def test_accepts_plain_and_short_qualified_prefix_only(self):
        for ok in ("Suggestion: x", "Suggestion (optional): x"):
            self.assertTrue(review.SUGGESTION_RE.match(ok), ok)
        for bad in ("it would be nice", "Suggestions: x", "Suggestion x", "Note: Suggestion: x"):
            self.assertFalse(review.SUGGESTION_RE.match(bad), bad)


class DiffParseTests(unittest.TestCase):
    def test_removed_line_starting_with_dashes_is_not_a_header(self):
        diff = (
            "diff --git a/x.sql b/x.sql\n--- a/x.sql\n+++ b/x.sql\n"
            "@@ -1,2 +1,2 @@\n--- old comment\n+-- new comment\n keep\n"
        )
        lines = review.parse_changed_lines(diff)
        self.assertEqual(lines["x.sql"], {"RIGHT": {1}, "LEFT": {1}})


class TemplateHardeningTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        sh(self.repo.path, "checkout", "-q", "main")
        (self.repo.path / "src" / "AGENTS.md").write_text("Use the repo logger.\n")
        (self.repo.path / "AGENTS.md").write_text("root guidance\n")
        (self.repo.path / "docs").mkdir()
        (self.repo.path / "docs" / "AGENTS.md").write_text("unrelated\n")
        sh(self.repo.path, "add", "-A")
        sh(self.repo.path, "commit", "-qm", "guidance on base")
        sh(self.repo.path, "checkout", "-q", "feature")
        sh(self.repo.path, "rebase", "-q", "main")
        code, out = self.repo.run("freeze", "--repo", str(self.repo.path), "--base", "main")
        self.assertEqual(code, 0, out)
        self.dir = Path(out["dir"])
        self.head = out["head"]
        self.repo.run("select", "--dir", str(self.dir))
        self.repo.run("validate-plan", "--dir", str(self.dir))
        self.plan = json.loads((self.dir / "plan.json").read_text())

    def tearDown(self):
        self.repo.close()

    def write(self, name, obj):
        p = self.dir / name
        p.write_text(json.dumps(obj))
        return str(p)

    def synth(self, findings=(), outcomes=(), **extra):
        body = {"kind": review.SYNTH_KIND, "reviewed_head": self.head, "coverage": "complete",
                "consolidated_findings": list(findings), "resolutions": [],
                "prior_outcomes": list(outcomes), "limitations": []}
        body.update(extra)
        return body

    def test_guidance_covers_changed_ancestors_only(self):
        ctx = json.loads((self.dir / "context.json").read_text())
        self.assertEqual(ctx["guidance"], ["src/AGENTS.md", "AGENTS.md"])

    def test_prompts_name_files_outputs_and_owned_gaps(self):
        code, out = self.repo.run("prompts", "--dir", str(self.dir))
        self.assertEqual(code, 0, out)
        sec = Path(out["parallel"]["security"]).read_text()
        self.assertIn("lenses/security.md", sec)
        self.assertIn("  - src/auth.py", sec)
        self.assertIn("src/AGENTS.md", sec)
        self.assertIn(str(self.dir.resolve() / "lens-security.json"), sec)
        stale = Path(out["generalist"]).parent / "retired-lens.md"
        stale.write_text("old")
        self.repo.run("prompts", "--dir", str(self.dir))
        self.assertFalse(stale.exists())
        gen = Path(out["generalist"]).read_text()
        self.assertIn("validation.json", gen)
        self.assertIn("synthesis.json", gen)

    def test_validation_json_reports_missing_lenses(self):
        f = self.write("lens-security.json", lens_result(self.head, "security"))
        code, out = self.repo.run("validate-lens", "--dir", str(self.dir), f)
        self.assertEqual(code, 1)
        self.assertIn("correctness", out["missing_lenses"])
        self.assertTrue((self.dir / "validation.json").exists())

    def test_synthesis_cannot_cite_unselected_lens(self):
        ctx = json.loads((self.dir / "context.json").read_text())
        f = blocker("security", supporting=["security", "made-up"])
        errs = review.synthesis_errors(self.synth([f]), ctx, review.selected_ids(self.plan))
        self.assertTrue(any("unselected" in e for e in errs))

    def test_follow_up_prior_blockers_need_outcomes_and_carry_forward(self):
        ctx = {"prior": {"findings": [blocker("security"), {**blocker("security", rid="x:s"), "severity": "suggestion"}]}}
        rid = blocker("security")["root_cause_id"]
        self.assertEqual(review.prior_coverage_gaps(ctx, [], []), [f"prior blocker {rid} has no outcome"])
        still = [{"root_cause_id": rid, "outcome": "still_present"}]
        self.assertIn("not carried", review.prior_coverage_gaps(ctx, still, [])[0])
        carried = [{**blocker("correctness", rid="c:new"), "merged_from": [rid]}]
        self.assertEqual(review.prior_coverage_gaps(ctx, still, carried), [])
        fixed = [{"root_cause_id": rid, "outcome": "fixed"}]
        self.assertEqual(review.prior_coverage_gaps(ctx, fixed, []), [])


class BaseRefTests(unittest.TestCase):
    def test_head_relative_bases_are_rejected(self):
        for bad in ("HEAD", "HEAD^", "HEAD~3", "@", "@~1", "HEAD@{1}"):
            self.assertTrue(review.HEAD_RELATIVE_RE.search(bad), bad)
        for ok in ("main", "origin/main", "a1b2c3d", "release/HEADLINE", "users/x/head-fix"):
            self.assertFalse(review.HEAD_RELATIVE_RE.search(ok), ok)


class AwkwardRepoTests(unittest.TestCase):
    """Encodings, path quoting and line endings seen in real C#/PHP/legacy repos."""

    def test_freeze_handles_encodings_odd_paths_crlf_and_renames(self):
        repo = Repo()
        try:
            p = repo.path
            (p / "legacy.php").write_bytes("<?php\n$name = 'caf\xe9';\n".encode("latin-1"))
            (p / "Old Name.cs").write_text("class A {}\n")
            sh(p, "add", "-A")
            sh(p, "commit", "-qm", "more base")
            sh(p, "branch", "-f", "main", "HEAD")
            (p / "legacy.php").write_bytes("<?php\n$name = 'na\xefve';\n".encode("latin-1"))
            sh(p, "mv", "Old Name.cs", "New Name.cs")
            (p / "Ünïcode Dir").mkdir()
            (p / "Ünïcode Dir" / "Ctrl.cs").write_bytes(b"class C\r\n{\r\n    int x = 1;\r\n}\r\n")
            (p / 'say "hi".php').write_text("<?php echo 1;\n")
            sh(p, "add", "-A")
            sh(p, "commit", "-qm", "awkward")
            code, out = repo.run("freeze", "--repo", str(p), "--base", "main")
            self.assertEqual(code, 0, out)
            ctx = json.loads((Path(out["dir"]) / "context.json").read_text())
            paths = {f["path"] for f in ctx["files"]}
            self.assertEqual(paths, {"legacy.php", "New Name.cs", "Ünïcode Dir/Ctrl.cs", 'say "hi".php'})
            renamed = next(f for f in ctx["files"] if f["path"] == "New Name.cs")
            self.assertEqual((renamed["status"], renamed["old_path"]), ("R", "Old Name.cs"))
            changed = review.parse_changed_lines(Path(ctx["diff_path"]).read_text())
            self.assertEqual(changed["Ünïcode Dir/Ctrl.cs"]["RIGHT"], {1, 2, 3, 4})
            self.assertEqual(changed['say "hi".php']["RIGHT"], {1})
            self.assertEqual(changed["legacy.php"], {"RIGHT": {2}, "LEFT": {2}})
        finally:
            repo.close()

    def test_unquote_git_path(self):
        self.assertEqual(review.unquote_git_path('"a/say \\"hi\\".php"'), 'a/say "hi".php')
        self.assertEqual(review.unquote_git_path('"b/caf\\303\\251.cs"'), "b/café.cs")
        self.assertEqual(review.unquote_git_path("a/With Space.cs\t"), "a/With Space.cs")
        self.assertEqual(review.unquote_git_path("/dev/null"), "/dev/null")


class TermMatchingTests(unittest.TestCase):
    def test_path_words_split_camel_snake_kebab(self):
        self.assertEqual(review.path_words("src/OAuthTokenRefresher.cs"),
                         {"src", "o", "auth", "token", "refresher", "cs"})
        self.assertEqual(review.path_words("db/add_user-roles.sql"), {"db", "add", "user", "roles", "sql"})

    def test_whole_word_prefix_and_substring_terms(self):
        words = review.path_words("src/PostAuthorProfile.cs")
        low = "src/postauthorprofile.cs"
        self.assertFalse(review.term_matches("auth", low, words))
        self.assertTrue(review.term_matches("author*", low, words))
        self.assertFalse(review.term_matches("token", "src/tokenizer.cs", review.path_words("src/Tokenizer.cs")))
        self.assertTrue(review.term_matches(".csproj", "src/app.csproj", review.path_words("src/App.csproj")))
        self.assertTrue(review.term_matches("migration*", "db/migrations/x.cs", review.path_words("db/Migrations/x.cs")))


if __name__ == "__main__":
    unittest.main()

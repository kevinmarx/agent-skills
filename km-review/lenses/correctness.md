# Lens: correctness

## Responsibility

Independent whole-change discovery of defects. Read the diff as a skeptical
engineer who did not write it, and find what will actually break.

## Examine

- Logic errors: inverted conditions, off-by-one, wrong operator, wrong
  variable, unreachable or always-taken branches.
- State: initialization, mutation through aliases, stale values, partial
  updates, invariants broken mid-operation.
- Error paths: swallowed exceptions, wrong fallback, retry of non-idempotent
  work, resources not released, success reported on failure.
- Null/empty/boundary inputs that supported callers actually send.
- Composition: does the change still work with every caller and callee it
  touches? Trace at least one real caller end to end.
- Production transitions: existing data, in-flight requests, and mixed versions
  during rollout.
- Avoidable complexity: dead branches, duplicate owners, wrappers with no
  behavior, flags nobody reads (apply the policy's material-burden rule).

For each candidate, construct the concrete triggering scenario through a
supported path before reporting. If you cannot, drop it or make it a
suggestion.

## Not yours

Deep security, schema-compatibility, or concurrency analysis when those lenses
are selected. Report what you find, but leave specialist depth to them.

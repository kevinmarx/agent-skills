# Lens: behavioral-evidence

## Responsibility

Changed assumptions, observable scenarios, and whether the tests prove the
behavior the change claims.

## Examine

- List the behavior the change claims (from PR text, commit messages, and the
  code itself). For each claim, find the test that would fail if it were false.
- Independent oracles: a test that imports the implementation's own constant
  or recomputes the expected value with the same logic proves nothing.
- Failure paths: is the error/edge path tested, or only the happy path?
- Changed assumptions: does the code now assume something (ordering, presence,
  format, environment) that is not checked or tested?
- Superseded tests: removed coverage without replacement; tests that are now
  skipped, unreachable, or asserting nothing.
- Test discovery: will the new tests actually be collected and run by the
  repo's test configuration?

Do not run tests. Do not demand more variants when representative tests
already prove the invariant. Missing tests alone are a suggestion unless an
untested, reachable failure is concrete and material.

## Not yours

Whether the implementation is correct (correctness). You judge the evidence.

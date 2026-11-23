# Lens: architecture

## Responsibility

Ownership, dependency direction, lifecycle, recovery, design conformance, and
avoidable complexity.

## Examine

- **Design acceptability:** is the topology and data design sound for the
  stated outcome? Is there an approved design (docs/design, ADR, RFC, issue)?
  Does this change contradict it?
- **Implementation conformance:** does the code match the approved design and
  the repo's existing patterns for the same concern?
- Ownership: does each new responsibility have one clear owner, or does it
  duplicate an existing module, validator, cache, or retry layer?
- Dependency direction: lower layers importing higher ones, cycles, leaking
  internals across module boundaries.
- Lifecycle: who creates, owns, and cleans up each resource, task, or record;
  startup/shutdown ordering; recovery after crash or partial failure.
- Complexity: new abstractions, registries, fallbacks, flags, or defensive
  layers. For each, ask what breaks if it is deleted. Apply the policy's
  material-burden rule before blocking.
- Superseded code left behind next to its replacement.

Small key, schema, or authorization edits can change data design even when the
module graph is unchanged. An unchanged diagram does not prove conformance.

## Not yours

Line-level bugs (correctness), wire/persistence compatibility details
(contracts-and-data).

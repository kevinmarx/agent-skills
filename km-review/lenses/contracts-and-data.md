# Lens: contracts-and-data

## Responsibility

API, schema, wire, and persisted-data contracts between producers and
consumers, including compatibility with data and clients that already exist.

## Examine

- Public and internal API changes: removed or renamed fields, changed types,
  changed defaults, changed error codes, changed semantics under the same name.
- Serialization: field names, casing, enum values, optional vs required,
  unknown-field handling, date/number formats.
- Persisted data: can the new code read every record the old code wrote? Can
  the old code (during rollback or rolling deploy) read what the new code
  writes? Are migrations reversible and safe to re-run?
- Message/queue payloads in flight across a deploy.
- Producer/consumer pairs: find every consumer of a changed contract and check
  each one.

Before requiring compatibility, name the supported producer and consumer
versions and why the obligation exists. Unreleased intermediate formats do not
acquire support by default. Persisted and security-relevant data always
matter.

If the author documents an intentional break, verify it against source. A
supported justification can make the finding a suggestion; it never
downgrades a break on a durable-state or safety path.

## Not yours

General design (architecture) or line-level logic (correctness).

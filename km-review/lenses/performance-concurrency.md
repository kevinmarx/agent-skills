# Lens: performance-concurrency

## Responsibility

Concurrency, ordering, retries, idempotency, capacity, and resource behavior.

## Examine

- Races: check-then-act, shared mutable state, missing locks or wrong lock
  scope, async interleavings, lost updates.
- Ordering assumptions across threads, processes, queues, or replicas.
- Retries: bounded? backoff? idempotent target? retry of an operation whose
  outcome is unknown?
- Duplicate delivery and at-least-once semantics.
- Resource lifetime: connections, file handles, timers, goroutines/tasks,
  subscriptions — released on every path including errors and cancellation.
- Capacity: unbounded collections, N+1 queries, per-request work that scales
  with total data, missing pagination, hot loops, synchronous I/O on hot
  paths.
- Timeouts and cancellation propagation.

Report performance only with a concrete reachable scale or workload. "Could be
slow" without one is a suggestion at most.

## Not yours

Functional logic unrelated to concurrency or load.

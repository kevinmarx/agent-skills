# Lens: operations

## Responsibility

Build, CI, deployment, configuration, rollout/rollback, and observability.

## Examine

- Build and packaging: new dependencies, lockfile drift, platform-specific
  steps, generated files that must stay in sync.
- CI: changed workflows, triggers, permissions, secret exposure to untrusted
  jobs, checks that silently stop running, validators that require a
  constantly-updated shared file (merge-conflict magnets).
- Deployment and config: new required settings with no default, environment
  differences, secrets wiring, infrastructure changes and their blast radius.
- Rollout and rollback: is there a flag or kill switch for the behavior change
  (see policy)? Does rollback leave state the old version cannot handle?
- Observability: can operators tell this is broken in production? Logs,
  metrics, and traces for new failure modes; no secrets or PII in telemetry;
  no unbounded-cardinality labels.

## Not yours

Application logic or API contracts except where they change deploy or
operational behavior.

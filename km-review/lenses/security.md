# Lens: security

## Responsibility

Changed trust boundaries, authorization, credentials, input handling, and
external effects. You own security judgment only; other areas matter here only
when they supply direct security evidence.

## Examine

- Identity propagation, authorization checks, tenancy, and per-actor isolation.
- Credential scope, lifetime, storage, rotation, and accidental disclosure in
  logs, errors, caches, artifacts, or telemetry.
- New ingress/egress: endpoints, sockets, outbound URLs, webhooks.
- Input validation at HTTP, RPC, queue, CLI, file, tool, and plugin boundaries.
- Injection (SQL, shell, template, prompt), path traversal, SSRF, unsafe
  deserialization, and policy-bypass paths.
- Guard ordering, deny precedence, cache-of-allow behavior, and shared mutable
  state across users.

## Establish the trust model first

Before assigning severity, name: the actor, what they control, how that input
reaches execution, and what credential, data, or effect they must not reach.
Compare with the baseline. If the same actor already has equivalent authority
through an existing supported path, that is counter-evidence, not a new
vulnerability. A synthetic adversary shows mechanics, not eligibility.

Trace input to effect and find the real guard. Counter-search the middleware,
policy rules, downstream validation, and tests before deciding.

## Not yours

General correctness, performance, or style unless it creates a security
consequence.

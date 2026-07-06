# Backend Reference

Use this reference for new Go backends or large backend reorganizations.

## Initial Setup

- Initialize the module at repo root with `go mod init <module>`.
- Create `cmd/<server>/main.go`, `internal/`, `internal/gen/`, `proto/`, and `migrations/`.
- Add ConnectRPC, generated proto packages, protovalidate, pgx/pgxpool, sqlx or sqlc, and goose only when the project needs the related capability.
- Keep environment/config loading in `internal/cfg`; fail fast on missing required config.

## Package Shape

Use vertical slices for feature-owned code:

```text
internal/features/billing/
  repository.go
  service.go
  server.go
```

Use shared platform packages only for cross-cutting concerns:

```text
internal/platform/db/
internal/platform/auth/
internal/platform/observability/
```

Avoid dumping feature logic into broad `service` or `repo` packages unless the target repo already uses that pattern.

## Server Wiring

- Build dependencies in `main`: config, logger, DB pool, migrations, repositories, services, servers.
- Create one root `http.ServeMux`.
- Build Connect handler options once, usually public and protected sets.
- Include `connect.WithRecover(...)` when the project has a panic handler.
- Include `connect.WithInterceptors(validate.NewInterceptor(), ...)`; auth and observability interceptors are project-specific.
- Register generated handlers with `New<Service>Handler(server, options...)`.
- Add `/healthz` or the project's readiness endpoint before wrapping middleware.
- Use `http.Server.Shutdown` with a timeout on SIGINT/SIGTERM.

## Data Access

- Use `pgxpool.Pool` for connection pooling.
- Use `stdlib.OpenDBFromPool` when a library needs `database/sql`.
- Use `sqlx` for pragmatic row scanning and named queries; keep SQL explicit.
- Use `sqlc` when the project already has it or the feature benefits from compile-time checked query types.
- Run goose migrations during startup only when that is the established project behavior.
- Keep transactions at the service layer when a use case spans multiple repository calls.

## sqlc

- Keep migrations as the schema source of truth; regenerate sqlc after migration or query changes.
- Keep handwritten query files with the owning feature, for example `internal/features/billing/queries/*.sql`.
- Generate sqlc code into a feature-local internal package such as `internal/features/billing/db`; follow the target repo's existing package name if present.
- Wrap generated `Queries` in the feature repository so services do not depend directly on sqlc types unless those types are intentional API.
- Use `pgx/v5` or the repo's existing sqlc driver. Pass `context.Context` and use `pgx.Tx`/sqlc `WithTx` patterns for transactions.
- Do not edit generated `*.sql.go` files. Change the migration or `.sql` query and regenerate.
- Prefer one named query per use case. Use `sqlx` or handwritten repository code for highly dynamic filters/reporting when sqlc would force awkward query generation.

## Transport Boundaries

- Transport servers should be thin adapters from generated request/response types to service calls.
- Use generated protobuf constructors/types instead of hand-rolled DTOs at RPC boundaries.
- Convert domain errors to `connect.NewError` at the boundary when clients need stable codes.
- Do not import frontend concepts into backend packages.

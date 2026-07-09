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
internal/platform/logging/
internal/platform/apperr/
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

## Logging

- Use `log/slog` as the backend logging API.
- Initialize logging once during startup, usually from `cmd/<server>/main.go` through `internal/platform/logging`.
- Support two initial modes:
  - `dev`: text logs to the console with color for local readability.
  - `prod`: JSON logs with no color for production log ingestion.
- Attach request IDs to request contexts in middleware or interceptors. Include the request ID in every request-scoped log record.
- Log every request once through middleware, including at least request path, request duration, source IP address, request ID, and user ID from the auth context when available.
- Capture request duration in the middleware that wraps the final handler. If useful, also capture status code by wrapping `http.ResponseWriter`.
- Resolve source IP consistently. Prefer a trusted proxy-aware helper for `X-Forwarded-For`/`Forwarded` only when the app is behind known proxies; otherwise use `RemoteAddr`.
- For background or async operations started by a request, carry the initiating request ID into the operation context or logger fields when applicable.
- Keep log calls out of ordinary repository/service error paths. Return wrapped errors upward and let the boundary that owns the operation log once.

## Application Errors

- Add a small global app-level error package, usually `internal/platform/apperr`, for user-safe errors.
- Prefer a type with only the fields the app actually needs by default:

```go
type Error struct {
	UserMessage     string
	InternalMessage string
}
```

- `UserMessage` is safe to show to users. `InternalMessage` is for logs and debugging context only.
- Do not start with numeric codes or broad categories unless a product/API contract later needs them.
- Anywhere in the app may create or wrap an app error with a user message.
- Always wrap errors with `%w` as they move through repository, service, background, and transport code:

```go
return fmt.Errorf("create invoice for account %s: %w", accountID, err)
```

- Avoid logging the same error at every layer. Bubble the wrapped error chain up and log it once at the owner boundary.
- At the transport boundary, inspect the error chain for the first app error with a `UserMessage`. Return that user message to the client.
- If no app error exists in the chain, return a generic user-safe message such as `An unknown error occurred`.
- Always log the full original error chain at the boundary with `slog.ErrorContext` so backend logs retain the traceable internal context.
- For background workers or async operations, the owner boundary is the worker/job runner. Log the full error once there, including the initiating request ID if there is one.

## Data Access

- Before scaffolding database code for a new project, ask the user to choose Postgres, SQLite, or SQL Server.
- Read the matching database reference before implementing repositories, migrations, or query generation:
  - `references/databases/postgres.md`
  - `references/databases/sqlite.md`
  - `references/databases/sql-server.md`
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
- Prefer one named query per use case. Use manual dynamic query builders for highly dynamic pagination, complex filters, or reporting when sqlc would force awkward query generation.

## Transport Boundaries

- Transport servers should be thin adapters from generated request/response types to service calls.
- Use generated protobuf constructors/types instead of hand-rolled DTOs at RPC boundaries.
- Convert app-level user-message errors to `connect.NewError` at the boundary.
- The transport error layer should log the full original error once, choose the first safe `UserMessage` from the wrapped chain, and map it to a Connect-friendly error.
- Use a generic Connect internal error message when no app-level user message is present.
- Do not import frontend concepts into backend packages.

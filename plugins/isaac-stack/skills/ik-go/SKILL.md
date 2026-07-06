---
name: ik-go
description: "Build, refactor, review, and scaffold Go backends using Isaac's conventions for ConnectRPC services, protovalidate, vertical feature slices, pgx/pgxpool, sqlx or sqlc data access, goose migrations, slog logging, config loading, and HTTP server lifecycle. Use when Codex is asked to create or change Go backend code, initialize a backend repo, wire ConnectRPC handlers, organize services/repositories, add SQL queries, or apply Isaac backend best practices."
---

# Go Backend

## Overview

Use this skill for Go backend work in Isaac-stack projects. Prefer the target repo's existing patterns; for new projects, read `references/backend.md`.

## Defaults

Use:

- `net/http`, `log/slog`, `context`, and graceful shutdown from the standard library.
- ConnectRPC generated handlers from `internal/gen`.
- `connectrpc.com/validate` with protovalidate on all RPC handlers.
- `pgx/v5/pgxpool` for Postgres connections, `sqlx` for pragmatic SQL mapping, `sqlc` for typed query generation when established or useful, and `goose` for migrations.
- Vertical feature packages under `internal/features/<feature>` for feature-owned repository, service, and server code.

Treat Azure identity, OpenTelemetry, background workers, and special CORS origins as project-specific hooks, not mandatory boilerplate.

## Structure

Use this shape unless the repo already has a stronger local convention:

```text
cmd/<server>/main.go
internal/cfg/
internal/features/<feature>/
internal/platform/
internal/transport/
internal/gen/
migrations/
```

Keep `cmd` thin: load config, initialize logger/DB/migrations/dependencies, register handlers, start and stop the server.

## Implementation Rules

- Keep generated protobuf/ConnectRPC code under `internal/gen`; never edit generated files.
- Keep generated sqlc code behind repositories; never edit generated SQL output files.
- Pass `context.Context` through every service and repository method that touches I/O.
- Keep repositories SQL-focused and services business-focused. Transport servers adapt RPC requests to services.
- Return useful errors and map them to Connect errors at the transport boundary when needed.
- Register public and protected handler option sets separately when auth differs.
- Put `validate.NewInterceptor()` in the ConnectRPC interceptor chain for both public and protected handlers.
- Add health/readiness endpoints and graceful shutdown for long-running servers.

## Validation

Run the narrowest meaningful checks:

```bash
go test ./...
go test ./internal/features/<feature>/...
go vet ./...
```

If proto contracts changed, regenerate bindings before running Go checks.

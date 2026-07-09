# SQLite

Use this reference after the user chooses SQLite for an Isaac-stack backend.

## Defaults

- Keep migrations as the schema source of truth.
- Prefer sqlc for SQLite-compatible typed query generation.
- Keep SQLite schema and query files compatible with the selected driver and sqlc engine.
- Keep feature-owned query files near the repository code, for example `internal/features/billing/queries/*.sql`.
- Generate sqlc output into a feature-local internal package such as `internal/features/billing/db`, unless the repo already has a stronger convention.
- Wrap generated `Queries` behind repository methods so service code does not depend on sqlc types by accident.

## Manual Queries

sqlc can handle most CRUD and fixed-shape list queries. For highly dynamic pagination, complex filters, and reporting queries, prefer explicit manual query builders in the repository when that keeps the code simpler and clearer.

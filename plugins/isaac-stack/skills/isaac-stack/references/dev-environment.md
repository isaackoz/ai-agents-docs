# Dev Environment

Use this reference when initializing Isaac-stack projects or adding shared local-development commands.

## Taskfile

Create a root `Taskfile.yml` for new projects unless the repo already has an equivalent command runner.

Include these tasks when applicable:

- `gen:proto`: generate protobuf, ConnectRPC Go, and ConnectRPC TypeScript bindings.
- `gen:sqlc`: generate sqlc output after migration or query changes.
- `dev:backend`: run the Go backend through `air` for hot reload.
- `dev:frontend`: run the SvelteKit/Vite frontend dev server with hot reload.
- `dev`: run `dev:backend` and `dev:frontend` together.

Prefer the target repo's existing ports and command style. Keep generation tasks as thin wrappers around the source tool, for example `cd proto && buf generate` or `sqlc generate`.

## Dev Servers

- Run the frontend through Vite in development so Svelte hot reload stays active.
- Configure the Vite dev server proxy for backend API/RPC paths, so browser calls go through the frontend origin during local development.
- Run the backend with `air` so Go code changes restart the server automatically.
- In dev mode, disable graceful shutdown and exit immediately when the process receives a stop signal or is restarted by `air`. Keep graceful shutdown enabled for production.

## Database Choice

When initializing a project with persistence, ask the user which database to use before scaffolding data access. Offer these choices:

- Postgres
- SQLite
- SQL Server

Load the matching backend database reference before implementing repositories, migrations, or generation:

- `ik-go/references/databases/postgres.md`
- `ik-go/references/databases/sqlite.md`
- `ik-go/references/databases/sql-server.md`

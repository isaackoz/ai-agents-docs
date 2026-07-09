# SQL Server

Use this reference after the user chooses SQL Server for an Isaac-stack backend.

## Defaults

- Do not use sqlc for SQL Server; sqlc does not support it.
- Use explicit repository methods with handwritten SQL.
- Keep SQL strings close to the repository methods that own them.
- Use clear scanning and parameter binding through the selected SQL Server driver.
- Keep migrations as the schema source of truth when the project uses migrations.

## Dynamic Queries

For pagination, complex filters, and reporting queries, use manual dynamic query builders in the repository. Keep builder inputs typed and avoid leaking SQL construction into service or transport code.

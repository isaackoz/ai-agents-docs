---
name: isaac-stack
description: "Coordinate Isaac's default application stack: Go backend, SvelteKit SPA frontend, ConnectRPC transport, Buf/protobuf contracts, protovalidate validation, and shared project setup. Use when Codex is asked to create, refactor, review, or plan a whole project or cross-stack feature that spans backend, frontend, and transport conventions."
---

# Isaac Stack

## Overview

Use this as the router for Isaac-stack projects. Load the focused domain skill before doing domain work:

- `ik-svelte` for Svelte 5, SvelteKit SPA setup, shadcn-svelte, TanStack Query/Form, and generated TS clients.
- `ik-connectrpc` for proto contracts, Buf generation, ConnectRPC wiring, and protovalidate.
- `ik-go` for Go backend setup, service organization, repositories, migrations, and HTTP server lifecycle.

## Defaults

Assume this repo shape unless the target project already differs:

```text
frontend/
proto/
cmd/
internal/
internal/gen/
migrations/
```

Use ConnectRPC as the frontend/backend transport unless the user explicitly says otherwise. Use protovalidate as the shared validation layer for proto request messages.

## Workflow

Inspect the target repo first. Preserve existing structure and scripts when they are already established.

For new projects, set up in this order:

1. Create the repo skeleton and Go module.
2. Create `proto/` and configure Buf/protovalidate.
3. Generate Go and TypeScript bindings.
4. Wire the Go ConnectRPC server.
5. Create the SvelteKit SPA and generated client/query/form usage.

When a change crosses boundaries, change the proto contract first, regenerate bindings, then update backend and frontend call sites.

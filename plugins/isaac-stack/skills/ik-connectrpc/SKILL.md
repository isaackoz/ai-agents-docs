---
name: ik-connectrpc
description: "Build, refactor, review, and scaffold ConnectRPC and protobuf transport for Isaac-stack projects. Use when Codex is asked to create or change proto contracts, Buf generation, protovalidate rules, generated Go or TypeScript bindings, ConnectRPC client/server wiring, RPC error handling, or frontend/backend transport conventions."
---

# ConnectRPC

Use ConnectRPC as the transport layer between the SvelteKit SPA and Go backend unless the user says otherwise. Use protovalidate as the shared validation layer.

## Defaults

Assume this repo shape unless the target repo differs:

```text
frontend/
proto/
cmd/
internal/
internal/gen/
```

Generated Go output belongs in `internal/gen`. Generated TypeScript output belongs in `frontend/src/lib/gen`. Do not edit generated files.

## Setup

For new projects:

1. Install the TS generator at repo root: `bun install @bufbuild/protoc-gen-es@latest`.
2. Create `proto/`.
3. Copy `references/buf.yaml` and `references/buf.gen.yaml` into `proto/`.
4. Replace the `go_package_prefix` placeholder in `buf.gen.yaml` with the target Go module plus `/internal/gen`.
5. Ensure Go generator tools are available through the target repo's normal tool setup.
6. Generate bindings with the existing script (`task genproto`, `make genproto`) or `cd proto && buf generate`.
7. For the server deployment, when using ConnectRPC follow the guidelines at https://connectrpc.com/docs/go/deployment for the http server setup, CORS, and timeouts.  

## Proto Rules

- Use versioned package paths, e.g. `proto/account/v1/account.proto` with `package account.v1`.
- Group services by vertical slice.
- Name RPCs with actions: `GetExample`, `CreateExample`, `ListExamples`.
- Name wrappers `<RpcName>Request` and `<RpcName>Response`.
- Add protovalidate rules to request fields unless the request intentionally has no fields.
- For enums, use `MY_ENUM_UNSPECIFIED = 0` and prefix later values with the enum name.
- Follow Buf `STANDARD` lint and `FILE` breaking checks.

## Usage

Backend:

- Use generated `*connect.New<Service>Handler` functions from `internal/gen`.
- Add `connectrpc.com/validate` with `validate.NewInterceptor()` to every handler option set.
- Keep transport servers thin; call services for business logic.

Frontend:

- Use generated TS schemas/types from `frontend/src/lib/gen`.
- For protobuf-backed forms, use generated schemas with protovalidate validators.
- Read `references/svelte-error-hook.md` when mapping `ConnectError` into SvelteKit app errors.

## Validation

After proto changes, regenerate bindings and run the narrowest checks for changed surfaces:

```bash
cd proto && buf lint && buf breaking --against '.git#branch=main'
go test ./...
cd frontend && bun run check
```

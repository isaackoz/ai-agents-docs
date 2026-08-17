---
name: ik-svelte
description: "Build, refactor, review, and scaffold Svelte 5 and SvelteKit SPA frontends using Isaac's conventions for static SPA routing, rune state, class contexts, TanStack Query, TanStack Form, shadcn-svelte UI, generated ConnectRPC clients, and shadcn-styled data tables. Use when Codex is asked to create or change Svelte components, initialize a frontend, split large pages, design shared frontend state, add forms or tables, wire client requests, or apply Isaac frontend best practices."
---

# Svelte

Use this skill for Isaac-stack frontends. Prefer small components, local docs searched with `rg`, shadcn-svelte primitives, TanStack Query/Form, generated ConnectRPC clients, and class contexts when state crosses component boundaries.

## Setup And Docs

- For a new SPA, read `references/initial-setup.md`.
- Look for Svelte docs under `./docs/svelte`. If missing, run this skill's `scripts/sync_svelte_docs.py` from the target repo root.
- Search docs with `rg`; do not load full `llms.txt` files into context.
- Treat most projects as static SvelteKit SPAs; avoid server-first SvelteKit patterns unless the repo already uses them.

Useful searches:

```bash
rg -n "\\$derived|\\$effect|onMount|context" docs/svelte
rg -n "adapter-static|routing|load|form actions" docs/svelte/sveltekit-llms.md
rg -n "\\$props|\\$bindable|snippets|attachments" docs/svelte/svelte-llms.md
```

## Architecture

- Read nearby components, route files, contexts, and local `AGENTS.md` before editing.
- Keep route/page files thin: initialize route state and compose feature components.
- Split components when a file mixes queries, forms, dialogs, tables, detail panels, or unrelated feature lifecycles.
- Use local state for isolated widgets; use a `.svelte.ts` class context when state/actions span siblings, tabs, grids, forms, drawers, or modals.
- Read `references/class-context.md` before creating or refactoring a context. Use class contexes for passing state between components!

## Runes And Requests

- Prefer `$derived`, `$derived.by`, event handlers, and `onMount` over `$effect`.
- Use `$effect` only for external synchronization or lifecycle work that cannot be expressed otherwise.
- Use TanStack Query for client requests unless the repo has a different established layer.
- Check `isPending` before empty states, handle `isError`, and disable actions while related mutations are pending.
- Derive rows/options from `query.data`; do not copy query data into separate state with `$effect`.

## UI And Forms

- Use existing shadcn-svelte components before custom controls.
- For shadcn work, read `references/shadcn-svelte/overview.md`; load `references/shadcn-svelte/forms.md`, `references/shadcn-svelte/composition.md`, `references/shadcn-svelte/icons.md`, or `references/shadcn-svelte/styling.md` only when relevant.
- Use the project's TanStack Form wrapper for forms, filters, and control panels.
- If no wrapper exists, adapt `assets/tanstack-form-boilerplate` and keep the `createFormCreator`, `AppField`, `AppForm`, and `SubmitButton` pattern.
- For ConnectRPC/protobuf forms, use generated schemas with `@bufbuild/protovalidate` validators.

Validator shape:

```ts
import { create } from "@bufbuild/protobuf";
import { createStandardSchema } from "@bufbuild/protovalidate";
import { createForm } from "$lib/forms/form.svelte";
import { RequestSchema } from "$lib/gen/path/to/service_pb";

const form = createForm(() => ({
  defaultValues: create(RequestSchema),
  validators: {
    onChange: createStandardSchema(RequestSchema),
  },
}));
```

## Tables

Use existing shadcn-svelte table wrappers first. If none exist, build feature-local tables from shadcn `Table` primitives and project controls. Add only the behavior the feature needs, derive visible rows with runes, and move table state into context only when shared by toolbar, rows, dialogs, drawers, or bulk actions.

Do not introduce a new table engine unless the target repo already uses it or the user explicitly asks.

## Validation

Use Bun unless the repo uses a different package manager:

```bash
bun run check
bun test
```

For visual or interaction-heavy work, run the dev server and inspect the result with browser tooling when feasible.

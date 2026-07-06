# shadcn-svelte Reference

Use this reference when adding, updating, fixing, or composing shadcn-svelte components.

## Workflow

1. Read the target project's `components.json`.
2. Resolve aliases from `components.json`; do not hardcode `$lib/components/ui` if the project uses a different alias.
3. List installed UI components before importing or adding a component.
4. Use the project's package runner for CLI commands: `bunx --bun shadcn-svelte@latest`, `pnpm dlx shadcn-svelte@latest`, or `npx shadcn-svelte@latest`.
5. After adding registry files, read the added files and fix imports/icons to match the project.

Never use `--overwrite` on `add` without explicit user approval.

## Imports

Multi-part components use namespace imports:

```ts
import * as Dialog from "$lib/components/ui/dialog";
import * as Card from "$lib/components/ui/card";
```

Single-component barrels use named imports:

```ts
import { Button } from "$lib/components/ui/button";
import { Input } from "$lib/components/ui/input";
```

## Defaults

- Use installed shadcn-svelte components before custom markup.
- Use built-in variants before custom styles.
- Use semantic tokens like `bg-background`, `text-muted-foreground`, and `text-destructive`.
- Use `svelte-sonner` for toasts when installed.
- Use the configured `iconLibrary` from `components.json` when present; otherwise inspect existing icon imports before adding new ones.

## Detailed Rules

- Read `forms.md` for Field, InputGroup, option sets, and validation state.
- Read `composition.md` for groups, overlays, cards, tabs, empty states, loading states, and feedback components.
- Read `icons.md` for icon imports and `data-icon` usage.
- Read `styling.md` for semantic colors, spacing, sizing, conditional classes, and z-index rules.

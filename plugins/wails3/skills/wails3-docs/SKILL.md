---
name: wails3-docs
description: "Build, refactor, review, migrate, package, and troubleshoot Wails v3 applications using current beta APIs and conventions. Use when working with the wails3 CLI, application managers, Go-to-frontend bindings and services, windows, menus, dialogs, events, streams, native desktop integrations, mobile targets, installers, updates, or Wails v2-to-v3 migrations."
---

# Wails 3

Use this skill as the source of truth for Wails v3. Do not substitute remembered Wails v2 APIs. This snapshot covers Wails `v3.0.0-beta.8` documentation at upstream commit `495a094dac8948d5ecc86c48e268cf69c3c13360` (2026-08-13). Treat beta and experimental APIs as changeable.

## Workflow

1. Inspect `go.mod`, `Taskfile.yml`, `build/config.yml`, `frontend/`, and generated bindings before changing an existing project.
2. Confirm the installed CLI and module version with `wails3 version` and `go list -m github.com/wailsapp/wails/v3` when available. If they differ from this snapshot, inspect local source or current upstream docs for changed signatures.
3. Read only the topic references needed for the task. For an unfamiliar API, also read [API reference](references/api-reference.md).
4. Preserve the project's frontend framework, package manager, Taskfiles, build configuration, and established service layout.
5. Implement Go services and application managers with `github.com/wailsapp/wails/v3/pkg/application`; regenerate bindings after changing bound methods or models.
6. Run the narrowest relevant validation: Go tests, frontend checks/tests, `wails3 generate bindings`, `wails3 dev`, `wails3 build`, or a platform packaging task.

## Defaults and guardrails

- Require Go 1.25+ for this snapshot. Install the CLI with `go install github.com/wailsapp/wails/v3/cmd/wails3@latest`.
- Use `application.New(application.Options{...})`, managers such as `app.Window` and `app.Event`, and services created with `application.NewService`.
- Call Go from generated frontend bindings. Do not add localhost HTTP solely to connect the frontend and backend.
- Treat services as singletons. Keep bound methods coarse-grained, validate all frontend-controlled input, return errors, and avoid chatty bridge calls.
- Use events for notifications and lifecycle signals; use streams for bidirectional byte traffic. Do not treat events as a request/response substitute when a bound method is clearer.
- Use hash-based frontend routing unless the chosen router is explicitly configured for an embedded asset server.
- Keep `OnWindowEvent` passive. Use `RegisterHook` when an event must be cancelled, such as preventing window close.
- Keep platform limitations explicit. Linux defaults to GTK4 + WebKitGTK 6.0; the `gtk3` compatibility tag is temporary through v3.0.x. Mobile, Wake, MCP control, and anything labeled experimental are not stable desktop APIs.
- Never edit generated frontend bindings. Regenerate them.

## Reference router

- **Install, initialize, CLI, templates, project layout:** [Setup and CLI](references/setup-cli.md)
- **Architecture, app construction, managers, lifecycle, assets:** [Core architecture](references/core-architecture.md)
- **Services, methods, models, enums, generated code:** [Bindings and services](references/bindings-services.md)
- **Custom/application events, streams, raw messages:** [Events and streams](references/events-streams.md)
- **Creation, options, multiple/frameless windows, hooks, permissions:** [Windows](references/windows.md)
- **Application/context menus, tray, accelerators, shortcuts:** [Menus and keyboard](references/menus-keyboard.md)
- **Native/custom dialogs, file and HTML drag-and-drop:** [Dialogs and drag-and-drop](references/dialogs-drag-drop.md)
- **Clipboard, browser, environment, screens, notifications, dock, autostart:** [System integrations](references/system-integrations.md)
- **Build configuration, cross-builds, signing, platform packaging:** [Build and packaging](references/build-packaging.md)
- **Updater, manifests, installers, associations, protocols, single instance:** [Distribution and updates](references/distribution-updates.md)
- **Debugging, unit/integration/E2E testing, panics, common failures:** [Development and testing](references/development-testing.md)
- **Frontend frameworks/routing, Gin, custom transport, server mode:** [Frontend and server integration](references/frontend-integration.md)
- **Input/data/network safety, profiling, optimization:** [Security and performance](references/security-performance.md)
- **iOS and Android:** [Mobile](references/mobile.md)
- **Wake and LLM/MCP control:** [Experimental features](references/experimental.md)
- **Consolidated Go, frontend runtime, manager, window, menu, dialog, and CLI signatures:** [API reference](references/api-reference.md)
- **v2 conversion, beta status, version drift, FAQ, targeted troubleshooting:** [Migration and troubleshooting](references/migration-troubleshooting.md)
- **Worked application patterns from official tutorials:** [Tutorial patterns](references/tutorial-patterns.md)

Search within references before loading several full files:

```bash
rg -n "WebviewWindowOptions|RegisterHook|PermissionCamera" references
rg -n "generate bindings|application.NewService|ServiceStartup" references
rg -n "updater|signing|AppImage|NSIS|MSIX" references
```

## Snapshot maintenance

Run `python3 scripts/audit_upstream.py` to compare the curated source inventory with current upstream `master`, or pass `--source-dir /path/to/wails` for a local checkout. The audit reports drift; it never rewrites curated documentation. Read `references/source-manifest.json` only when auditing coverage or updating this snapshot.

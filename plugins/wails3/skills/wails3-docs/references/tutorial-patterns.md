# Official Tutorial Patterns

Use this reference to choose an end-to-end example shape without loading full tutorial prose. Adapt patterns to the target repo; do not copy generated bindings or stale package names.

Sources: [tutorial overview](https://v3.wails.io/tutorials/overview/), [QR service](https://v3.wails.io/tutorials/01-creating-a-service/), [TODO app](https://v3.wails.io/tutorials/02-todo-vanilla/), [notes app](https://v3.wails.io/tutorials/03-notes-vanilla/), [self-updating app](https://v3.wails.io/tutorials/04-self-update-a-wails-app/), [first app](https://v3.wails.io/quick-start/first-app/), [first application](https://v3.wails.io/getting-started/your-first-app/), [next steps](https://v3.wails.io/quick-start/next-steps/), [why Wails](https://v3.wails.io/quick-start/why-wails/).

## Greeting/first app

Use for a new project or bridge smoke test:

1. `wails3 init -n <name> -t <framework>`.
2. Define one small Go service with an exported method.
3. Register it with `application.NewService`.
4. Generate bindings and call the method from a button/form.
5. Run `wails3 dev`, then `wails3 build` and launch the production artifact.

This proves toolchain, asset output, service generation, frontend import, promise/error handling, and production embed in the fewest moving parts.

## QR code service

Use for a service that depends on a Go library and returns generated data. Keep encoding/rendering logic in Go, validate input and size/error cases, return a frontend-friendly representation, and unit-test the service without a webview. This pattern demonstrates adding Go dependencies and exposing one cohesive capability rather than low-level library calls.

## TODO app

Use for shared in-memory CRUD state:

- protect service state with a mutex because bindings can be concurrent;
- expose `List`, `Create`, `Update/Toggle`, and `Delete/Clear` domain methods;
- use stable IDs, validate text/IDs, and return copies/DTOs rather than mutable internal slices;
- keep frontend pending/error/empty state explicit;
- emit a state-invalidated event only when multiple windows/independent consumers need it.

Extend with persistence behind a repository so service tests can use memory and production can use file/database storage.

## Notes app

Use for native file operations:

- select/open/save paths through native dialogs;
- use JSON tags for model mapping;
- validate/canonicalize paths and handle cancellation distinctly from failure;
- debounce autosave in the frontend or serialize it in a Go owner so older writes cannot overwrite newer state;
- use atomic writes and surface recoverable errors;
- track dirty state and cancel window close with `RegisterHook` when necessary.

This is the most relevant tutorial for dialogs, filesystem boundaries, serialization, and unsaved-change lifecycle.

## Self-updating app

Use for release infrastructure, not as a first ordinary feature:

- inject a valid SemVer current version;
- choose/configure a provider and distinguish app payloads from installers;
- pin a public key and sign final release bytes for tamper resistance;
- use built-in/custom/headless update UI through exported updater events;
- test from a previous installed version and verify restart/swap behavior;
- keep private signing keys only in CI secret storage.

Read [Distribution and updates](distribution-updates.md) before implementing this tutorial pattern.

## Selecting the next reference

- Add methods/models: [Bindings and services](bindings-services.md)
- Share progress/state: [Events and streams](events-streams.md)
- Add window/dialog/menu behavior: [Windows](windows.md), [Dialogs](dialogs-drag-drop.md), [Menus](menus-keyboard.md)
- Persist/distribute/update: [Security](security-performance.md), [Build](build-packaging.md), [Distribution](distribution-updates.md)

Tutorials teach a vertical slice, not every production requirement. Add validation, cancellation, logging, secure storage, platform testing, and release checks appropriate to the actual application.

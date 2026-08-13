# Development, Testing, Debugging, and Failures

Use this reference for the feedback loop, service/frontend/E2E tests, tracing, panic policy, diagnostics, and targeted platform troubleshooting.

Sources: [testing](https://v3.wails.io/guides/testing/), [E2E testing](https://v3.wails.io/guides/e2e-testing/), [debugging](https://v3.wails.io/guides/dev/debugging/), [panic handling](https://v3.wails.io/guides/panic-handling/), [FAQ](https://v3.wails.io/faq/), [macOS syso](https://v3.wails.io/troubleshooting/mac-syso/), [Windows RDP](https://v3.wails.io/troubleshooting/windows/rdp/).

Contents: [Validation](#validation-ladder) · [Go tests](#service-and-integration-tests) · [Frontend](#frontend-tests) · [E2E](#end-to-end-tests) · [Debugging](#debugging) · [Panics](#panics) · [Diagnostics](#common-diagnostic-map) · [Platform fixes](#macos-syso-failure)

## Validation ladder

Choose the narrowest checks that exercise the changed surface:

```bash
go test ./...
go test -race ./...
go test -cover ./...

cd frontend
npm test                 # or the project's package manager/script
npm run check

wails3 generate bindings # when bridge contracts changed
wails3 dev               # manual integration/native behavior
wails3 build              # production asset/embed/build path
```

Add platform packaging/install tests for menus, protocols, associations, notifications, permissions, signing, updater, and installer behavior. A browser-only test cannot prove native integration.

## Service and integration tests

Keep core services independent of `application.App` when possible: inject repositories, clocks, file systems, and integration adapters through narrow interfaces. Unit-test exported bound methods directly, including invalid input, cancellation, concurrency, and error mapping. Run the race detector for singleton services with mutable state.

Integration-test actual serialization-sensitive models, database/filesystem adapters in temporary locations, and application-manager wrappers behind fakes where native UI is not required. Do not start a webview for ordinary business logic tests.

## Frontend tests

Mock generated binding modules at the module boundary with Vitest/Jest equivalents. Test pending, success, empty, and rejected-promise behavior. Mock the Wails event runtime and verify subscription cleanup. Avoid reproducing Go business logic in mocks; use fixtures that express only the transport contract.

Keep generated bindings out of manual test edits. Regenerate them in CI or assert the worktree stays clean after generation so drift is detected.

## End-to-end tests

The official guide demonstrates Playwright against a development web server for complete frontend flows. This validates UI/routing and mocked/browser-visible interfaces, but native Wails dialogs and multi-window behavior may require a packaged/running Wails process and OS-specific automation. Separate:

- web E2E for DOM/routing/form flows;
- Go integration tests for services;
- native smoke tests for window, menu, dialog, tray, file-open, updater, and packaging behavior.

Use stable accessible locators, deterministic test data, isolated temp directories, and CI artifacts (screenshots/traces/logs) on failure. Do not let tests click real destructive OS prompts or publish/update production resources.

## Debugging

Start with:

1. `wails3 doctor` and version/module inspection.
2. Terminal output from `wails3 dev` and browser devtools console/network.
3. Generated bindings and application registration.
4. Narrow Go/frontend tests and race detector.
5. Taskfile dry/verbose output for build issues.

Use structured application logging with operation/window/service identifiers, but redact tokens, paths containing user data, clipboard content, updater authorization, and message payload secrets.

For Go performance, collect `runtime/trace` around a bounded reproducible operation, stop/close the trace cleanly, then inspect with `go tool trace trace.out`. Use `pprof` only through a controlled debug surface; never expose diagnostics unintentionally in production/server builds.

## Panics

Wails converts a panic from a frontend-invoked bound method into a rejected call instead of terminating the app. A configured `application.Options.PanicHandler` also observes it for logging or telemetry; without a custom handler, Wails logs that bound-method panic. Other recovered internal runtime panics go through the same custom handler, while the default internal panic path logs and quits. A custom handler may log/report/show safe UI and choose shutdown behavior:

```go
app := application.New(application.Options{
    PanicHandler: func(details *application.PanicDetails) {
        logger.Error("wails panic",
            "error", details.Error,
            "time", details.Time,
            "stack", details.StackTrace)
    },
})
```

The Wails handler does not automatically cover arbitrary background goroutines. Recover at an intentional goroutine owner boundary, capture stack/context, cancel dependent work, and decide whether the process remains safe. Prefer returning errors; do not use recovery to continue after corrupted invariants.

## Common diagnostic map

| Symptom | Checks |
|---|---|
| Missing/stale frontend call | Service registration, exported signature, generation patterns/output, regenerate bindings |
| Event not firing | Exact name/constant, direction/window scope, subscription timing, cleanup, runtime readiness |
| Blank production window | Frontend build output, embed path, asset handler, base URLs, hash routing |
| Dev works/build fails | Production frontend build, Taskfile/config, embedded files, platform build tags |
| Linux compile failure | `wails3 doctor`, GTK4/WebKitGTK 6 packages or deliberate `gtk3` tag |
| Native feature differs | Verify platform support/permissions/entitlements and test on the target OS |
| Cross-build fails | Docker image/daemon, CGO compiler, GOOS/GOARCH task variables |

## macOS `.syso` failure

Windows resource `.syso` files left in the project root may be selected during macOS builds. Remove stale generated files or name custom resources with Windows-specific suffixes such as `wails_windows_<arch>.syso` so Go build constraints exclude them. Regenerate Windows resources through the project task rather than leaving ambiguous files.

## WebView2 stalls over RDP

If popup/window operations stall for seconds after an RDP session changes monitor DPI, enable visual hosting before `app.Run()`:

```go
app := application.New(application.Options{
    Windows: application.WindowsOptions{
        UseVisualHosting: true,
    },
})
```

This switches WebView2 hosting before environment initialization. Setting it later has no effect. Enable it for affected RDP deployments, not reflexively for every application; regression-test rendering/input because hosting mode changes native composition behavior.

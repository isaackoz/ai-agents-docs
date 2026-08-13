# Migration, Beta Status, and Troubleshooting

Use this reference to migrate Wails v2 code, evaluate beta compatibility, detect stale knowledge, and diagnose common version/platform failures.

Sources: [v2-to-v3 migration](https://v3.wails.io/migration/v2-to-v3/), [roadmap/status](https://v3.wails.io/status/), [changelog](https://v3.wails.io/changelog/), [FAQ](https://v3.wails.io/faq/), [macOS syso](https://v3.wails.io/troubleshooting/mac-syso/), [Windows RDP](https://v3.wails.io/troubleshooting/windows/rdp/).

## Beta contract in this snapshot

Wails `v3.0.0-beta.8` was current on 2026-08-13. The beta compatibility promise covers desktop Windows/macOS/Linux amd64/arm64 with Go 1.25+. Windows uses WebView2; Linux defaults to GTK4 + WebKitGTK 6.0. The legacy `gtk3` tag lasts through v3.0.x and is removed in v3.1. Android/iOS do not block desktop stability and remain experimental. Beta APIs aim for stability, but prerelease defects and announced changes may still be corrected.

Beta.8 introduced desktop/server streams and included fixes around WebView2 initialization, ordered event delivery/backpressure, menus, Linux build baselines, and iOS linking. Do not assume an alpha/beta.1 project has these semantics.

Check actual versions:

```bash
wails3 version
go list -m github.com/wailsapp/wails/v3
go env GOMOD
rg -n 'wails/v2|wailsjs|pkg/runtime|wails\.json' .
```

If later than this snapshot, run the skill audit/current docs and inspect relevant Go/TypeScript declarations. If earlier, avoid using newly documented APIs until the module/CLI are upgraded together.

## v2-to-v3 mapping

| Wails v2 | Wails v3 |
|---|---|
| `wails.Run(&options.App{...})` | `application.New(Options)`, create windows, `app.Run()` |
| `Bind: []interface{}{...}` | `Services: []application.Service{application.NewService(...)}` |
| startup context stored on app struct | explicit dependencies and service lifecycle |
| global `runtime.Window*` with context | methods on window/app managers |
| `runtime.EventsEmit/On` | `app.Event` and frontend `Events` |
| single implicit window | first-class `WebviewWindow` objects and manager |
| `wailsjs/go/...` imports | generated `frontend/bindings/...` imports |
| `wailsjs/runtime/runtime` | `@wailsio/runtime` |
| v2 option packages/assetserver | `application.Options`, `AssetOptions`, platform structs |
| v2 JSON/project build config | v3 `Taskfile.yml` plus `build/config.yml` |
| CLI `wails` | CLI `wails3` |

## Migration sequence

1. Create a branch and make the v2 app/tests clean first.
2. Update module/CLI to `github.com/wailsapp/wails/v3`; remove v2-only option/runtime imports.
3. Rebuild `main` as composition root: dependencies, services, `application.New`, asset handler, windows, `Run`.
4. Convert bound structs to services. Remove stored runtime context; inject `*application.App` only where manager access is genuinely needed.
5. Map every global runtime call to an app/window/manager method.
6. Rebuild menus, dialogs, tray, lifecycle, and events with v3 types; add multi-window ownership explicitly.
7. Replace frontend imports with generated v3 bindings and `@wailsio/runtime`; clean up event subscriptions.
8. Replace build configuration/scripts with v3 Taskfiles and `build/config.yml`; reapply icons, product metadata, protocols, associations, signing, and installer customization.
9. Regenerate bindings, compile/test each platform, then package/install test.

Do not perform a blind identifier rename. v3 has different ownership, lifecycle, error, and multi-window semantics. Use the focused references while migrating each subsystem.

## Migration checks

- All services are registered once and mutable state is synchronized.
- Asset embed path matches the frontend production output.
- Every window has deliberate identity, lifecycle, close/quit policy, and platform options.
- No v2 `context.Context` is retained merely to call runtime globals.
- Frontend binding paths are imported from actual generated output.
- Events use exact v3 names/constants and subscriptions are disposed.
- Native dialogs/menus/tray/autostart/permissions are tested on target OSes.
- Build/package/sign output comes from v3 tasks under `bin/`.
- Old `wailsjs`, build files, generated resources, and `.syso` artifacts are removed only after replacements work.

## Common problems

### Missing bindings

Run `wails3 generate bindings`, verify exported supported signatures/service registration/package patterns/output directory, then update frontend imports. Ensure CLI and Go module versions agree and generated files are not shadowed by stale v2 `wailsjs` output.

### Context/runtime calls fail

Replace v2 global runtime functions with the manager/window that owns the operation. Pass the app/window explicitly to a service or look up the current/named window at operation time. Avoid one global current window in a multi-window app.

### Events do not arrive

Confirm direction, exact name/constant, payload shape, window versus app scope, runtime readiness, and listener lifetime. `Events.Off` removes by event name; retain the unsubscribe from `On` for one callback. Use `RegisterHook` for cancellation.

### Production window is blank

Check frontend build success/output, `go:embed`, asset handler, relative Vite base, and hash routing. Dev-server success does not validate embedded production assets.

### Platform build breaks

- Run `wails3 doctor`.
- Linux: install matching GTK4/WebKitGTK 6.0 dev packages or deliberately build supported v3.0.x with `-tags gtk3`.
- macOS: remove ambiguous Windows `.syso` files or name them with Windows-specific suffixes.
- Windows over RDP: for multi-second DPI-related WebView2 stalls, set `application.Options.Windows.UseVisualHosting` before `app.Run()`.
- Cross-build: verify Docker image/daemon, CGO compiler, GOOS/GOARCH task variables, and native signing requirements.

### Beta API mismatch

Use `go doc`, compiler errors, current examples, and generated TS declarations. Check upstream changelog/docs diff rather than forcing this snapshot’s signature. Run `python3 scripts/audit_upstream.py` when maintaining the skill.

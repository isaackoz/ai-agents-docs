# Core Architecture and Lifecycle

Use this reference for application construction, native asset delivery, managers, services at startup/shutdown, window lifecycle, and architectural decisions.

Sources: [architecture](https://v3.wails.io/concepts/architecture/), [bridge](https://v3.wails.io/concepts/bridge/), [lifecycle](https://v3.wails.io/concepts/lifecycle/), [build system](https://v3.wails.io/concepts/build-system/), [Manager API](https://v3.wails.io/concepts/manager-api/), [architecture patterns](https://v3.wails.io/guides/architecture/), [Application API](https://v3.wails.io/reference/application/).

Contents: [Runtime](#runtime-model) · [Minimal app](#minimal-application) · [Lifecycle](#lifecycle) · [Managers](#manager-selection) · [Bridge](#bridge-and-concurrency) · [Patterns](#architecture-patterns) · [Security](#security-boundary) · [Build](#build-system-mental-model)

## Runtime model

Wails compiles one Go backend and renders its web frontend in the OS webview: WebView2 on Windows, WebKit on macOS, and WebKitGTK on Linux. The frontend and Go code communicate through an in-process bridge using generated bindings. Production frontend assets are embedded/served by the application; development normally proxies to Vite.

Use these layers:

- `application.App`: owns lifecycle, services, assets, logger, raw routes, and platform configuration.
- Managers on the app: `Window`, `Event`, `Menu`, `ContextMenu`, `KeyBinding`, `GlobalShortcut`, `Browser`, `Env`, `Dialog`, `Screen`, `Clipboard`, `SystemTray`, and `Autostart`.
- Services: application business capabilities exposed through generated frontend bindings.
- Windows: native shells around webview content; multiple windows share the app and services.

## Minimal application

```go
package main

import (
    "embed"
    "log"

    "github.com/wailsapp/wails/v3/pkg/application"
)

//go:embed all:frontend/dist
var assets embed.FS

func main() {
    app := application.New(application.Options{
        Name: "Example",
        Assets: application.AssetOptions{
            Handler: application.AssetFileServerFS(assets),
        },
        Services: []application.Service{
            application.NewService(&GreetService{}),
        },
    })

    app.Window.NewWithOptions(application.WebviewWindowOptions{
        Name:  "main",
        Title: "Example",
        Width: 1000,
        Height: 700,
        URL:   "http://wails.localhost/",
    })

    if err := app.Run(); err != nil {
        log.Fatal(err)
    }
}
```

Use the template’s existing embed path and handler; frontend output directories differ. Asset configuration belongs on `application.Options.Assets`, not `WebviewWindowOptions`.

## Lifecycle

1. Construct dependencies and service instances.
2. Call `application.New` with options and services.
3. Create windows and register event/hooks.
4. Call `app.Run()` on the main goroutine. It starts services and the native event loop and blocks until shutdown.
5. On quit, Wails evaluates quit policy/hooks, closes windows, shuts down services, invokes shutdown callbacks, and releases platform resources.

Use service lifecycle interfaces when resources belong to a service. Keep database pools, background-worker cancellation, and other state on the service. Start workers once, propagate cancellation, and make shutdown idempotent. Use application-level `ShouldQuit`, `OnShutdown`, and `PostShutdown` options/hooks only for application-owned policy or ordering.

On macOS, closing the last window does not necessarily quit. Configure the Mac application behavior or expose a Quit menu action deliberately.

## Manager selection

| Need | API |
|---|---|
| Create/find windows | `app.Window` |
| App and custom events | `app.Event` |
| App menu | `app.Menu` |
| DOM-associated context menu | `app.ContextMenu` |
| In-app key bindings | `app.KeyBinding` |
| System-wide shortcuts | `app.GlobalShortcut` |
| Native dialogs | `app.Dialog` |
| External URL/file opening | `app.Browser` |
| OS/theme/debug information | `app.Env` |
| Monitor geometry | `app.Screen` |
| Text clipboard | `app.Clipboard` |
| Tray icon/menu | `app.SystemTray` |
| Login launch | `app.Autostart` |

Favor manager methods over v2-style global runtime calls. Managers make ownership and IDE discovery explicit.

## Bridge and concurrency

Generated frontend calls return promises. Bound Go methods execute concurrently; protect shared mutable service state and avoid assuming frontend call order. Keep payloads serializable and make long work cancellation-aware where the API permits it.

Good boundary design:

- Expose domain operations, not every repository method.
- Batch lists/updates to reduce bridge overhead.
- Return stable DTOs rather than leaking internal Go types.
- Use `(value, error)` for fallible calls; errors reject the frontend promise.
- Use events for progress and invalidation; use streams for continuous bytes.
- Test service logic directly in Go without starting a webview.

## Architecture patterns

- Small app: construct repositories/services in `main`, register services, create one window.
- Larger app: split domain services by responsibility, inject dependencies through constructors, and keep `main` as composition root.
- Multi-window app: services remain shared singletons; keep window-specific state in frontend stores or an explicit Go window/session registry.
- HTTP integration: use service HTTP routes or the application asset/route hooks only when a real HTTP interface is needed. Do not add Gin just to call Go from the Wails frontend.

## Security boundary

The webview frontend is not trusted input merely because it ships with the app. Validate paths, URLs, identifiers, and structured input in Go. Avoid loading untrusted remote pages into a privileged window. Grant web capabilities per window and expose only required service methods. Generated bindings improve typing, not authorization.

## Build system mental model

Wails analyzes registered services/models, generates bridge code and frontend bindings, builds frontend assets, compiles Go/native integrations, and packages through Taskfile tasks. Development replaces embedded production assets with the configured dev server. Treat `Taskfile.yml` and `build/config.yml` as project-controlled build interfaces rather than hidden CLI internals.

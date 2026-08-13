# Windows

Use this reference for creating and controlling webview windows, selecting options, multi-window ownership, frameless chrome, permissions, native events, and platform-specific settings.

Sources: [basics](https://v3.wails.io/features/windows/basics/), [options](https://v3.wails.io/features/windows/options/), [permissions](https://v3.wails.io/features/windows/permissions/), [multiple windows](https://v3.wails.io/features/windows/multiple/), [frameless windows](https://v3.wails.io/features/windows/frameless/), [events](https://v3.wails.io/features/windows/events/), [customizing windows](https://v3.wails.io/guides/customising-windows/), [Window API](https://v3.wails.io/reference/window/).

Contents: [Create](#create-and-find-windows) · [Options](#option-families) · [Events](#events-and-close-policy) · [Multi-window](#multi-window-patterns) · [Frameless](#frameless-windows) · [Permissions](#permissions) · [Failures](#platform-notes-and-failure-modes)

## Create and find windows

```go
mainWindow := app.Window.NewWithOptions(application.WebviewWindowOptions{
    Name:              "main",
    Title:             "My App",
    Width:             1100,
    Height:            760,
    MinWidth:          720,
    MinHeight:         480,
    InitialPosition:   application.WindowCentered,
    BackgroundColour:  application.NewRGB(24, 24, 27),
    URL:               "http://wails.localhost/",
})

window, ok := app.Window.GetByName("main")
windows := app.Window.GetAll()
current := app.Window.Current()
```

Give durable, unique names to windows that must be retrieved. `New()` uses defaults. `NewWithOptions` configures initial state. Assets are application-level, not a window option.

Useful controls include `Show`, `Hide`, `Close`, `Focus`, `Center`, `SetTitle`, `SetSize`, `SetMinSize`, `SetMaxSize`, `SetPosition`, `Minimise`, `Maximise`, `Fullscreen`, their inverse/toggle/query methods, `SetURL`, `SetHTML`, `Reload`, `SetEnabled`, `SetResizable`, `SetAlwaysOnTop`, `SetBackgroundColour`, and `Print`. There is no v3 `Destroy()`; use `Close()`.

## Option families

Core `WebviewWindowOptions` covers:

- identity/content: `Name`, `Title`, `URL`, `HTML`;
- size/position: width/height, min/max constraints, `InitialPosition`, X/Y;
- initial state: hidden, frameless, resize, always-on-top, start state;
- appearance: background color/type and application-menu use;
- input/security: file drop, content protection, permissions;
- button states and OS-specific `Mac`, `Windows`, and `Linux` structs.

Set `InitialPosition: application.WindowXY` when providing X/Y; centered is otherwise the default and coordinates are ignored. Prefer `application.NewRGB`/`NewRGBA` over manually populating `RGBA`.

Per-window platform structs are `application.MacWindow`, `application.WindowsWindow`, and `application.LinuxWindow`. Do not confuse them with application-level `MacOptions`, `WindowsOptions`, or Linux options. Windows backdrop constants are `application.Auto`, `None`, `Mica`, `Acrylic`, and `Tabbed`.

## Events and close policy

```go
offResize := window.OnWindowEvent(events.Common.WindowDidResize,
    func(e *application.WindowEvent) { saveGeometry(window) })

offClose := window.RegisterHook(events.Common.WindowClosing,
    func(e *application.WindowEvent) {
        if hasUnsavedChanges() {
            e.Cancel()
        }
    })

_ = offResize
_ = offClose
```

`OnWindowEvent` observes focus, lifecycle, move/resize, minimize/maximize/fullscreen, file drop, and other native events. `RegisterHook` intercepts cancellable events. Keep returned unsubscribe functions and release them with the owning component/service.

`app.Window.OnCreate` receives the registered window object during `NewWithOptions`, before the window is run and before its frontend runtime is ready in the pinned source. Use it to attach policy/listeners to every new window. Listen for `events.Common.WindowRuntimeReady` before operations that require the frontend runtime; some beta prose incorrectly describes `OnCreate` itself as post-runtime.

## Multi-window patterns

- Keep singleton windows in a field/registry. If present, focus/show instead of creating another.
- Clear registry references in a closing listener so a later action can recreate the window.
- Give document windows stable unique names and keep per-document state explicit.
- Share backend services across windows; broadcast with `app.Event.Emit` or target one window with `window.EmitEvent`.
- Do not retain closed window pointers in maps or goroutines.
- `WebviewWindowOptions` has no `Parent`. `parent.AttachModal(child)` provides sheet/modal attachment on supported platforms; Wails documents this primarily for macOS and it is not portable Windows/Linux modal behavior.
- Configure macOS last-window quit behavior deliberately.

## Frameless windows

Set `Frameless: true`, then provide accessible HTML/CSS chrome. Mark drag regions with the Wails-supported app-region CSS and exclude buttons/inputs from dragging. Implement close/minimize/maximize through a bound Go service or frontend runtime Window API. Ensure keyboard access, focus styles, double-click behavior, resizing, and high-DPI hit targets.

Transparent/translucent backgrounds and rounded/native backdrops vary by OS. Linux supports solid backgrounds in the documented option matrix. On Windows, choose between WebView2 app-region behavior and native non-client/caption features based on whether native snap layouts and caption behavior are required. Test on each target rather than assuming CSS chrome is identical.

## Permissions

Grant or deny web capabilities per window:

```go
Permissions: map[application.PermissionType]application.Permission{
    application.PermissionMicrophone: application.PermissionAllow,
    application.PermissionCamera:     application.PermissionAllow,
}
```

Permission types include microphone, camera, geolocation, notifications, and clipboard read where supported. Values allow, deny, or defer/default according to the current API. Platform behavior differs:

- Windows: declaring entries disables the older blanket grant behavior; omitted capabilities may prompt. List required capabilities explicitly. WebView2-specific permissions can be set under `WindowsWindow.Permissions` for unsupported cross-platform kinds.
- macOS: application entitlements and `Info.plist` usage descriptions/TCC consent are still required. A Wails map cannot bypass OS privacy policy.
- Linux: camera/microphone support is implemented; unsupported permission kinds remain denied.

Grant the minimum capability and do not load untrusted remote content in a privileged window.

## Platform notes and failure modes

- App icon is generally application-level (`app.SetIcon`); there is no portable per-window `SetIcon`. Linux has a creation option.
- Window menu/button/backdrop/titlebar APIs are platform-specific; guard behavior and provide fallbacks.
- Window does not show: check `Hidden`, call `Show`, and verify URL/assets/dev-server availability.
- Wrong X/Y: set `InitialPosition: WindowXY` and account for logical versus physical pixels.
- Close cancellation fails: use `RegisterHook`, not `OnWindowEvent`.
- Frameless window cannot drag/resize: verify app-region CSS, interactive exclusions, and platform-specific non-client mode.
- Permission still denied: check both Wails window policy and OS entitlements/usage strings/user settings.

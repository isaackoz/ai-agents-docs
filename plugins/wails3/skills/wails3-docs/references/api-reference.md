# Consolidated Wails v3 API Reference

Use this reference to choose the right public surface and verify common method shapes. It is a navigation aid, not a replacement for the installed Go/TypeScript definitions. Beta APIs can change; use `go doc`, IDE completion, generated bindings, `wails3 --help`, and current upstream source when signatures disagree.

Sources: [API overview](https://v3.wails.io/reference/overview/), [Application](https://v3.wails.io/reference/application/), [Window](https://v3.wails.io/reference/window/), [Menu](https://v3.wails.io/reference/menu/), [Events](https://v3.wails.io/reference/events/), [Dialogs](https://v3.wails.io/reference/dialogs/), [frontend runtime](https://v3.wails.io/reference/frontend-runtime/), [CLI](https://v3.wails.io/reference/cli/), [update manifest](https://v3.wails.io/reference/update-manifest/), [Manager API](https://v3.wails.io/concepts/manager-api/).

Contents: [Packages](#packages-and-discovery) · [Application](#application) · [Windows](#windows) · [Events](#events) · [Menus](#menus-and-tray) · [Dialogs](#dialogs) · [Frontend](#frontend-runtime) · [CLI](#cli-groups) · [Stability](#stability)

## Packages and discovery

Primary imports:

```go
import (
    "github.com/wailsapp/wails/v3/pkg/application"
    "github.com/wailsapp/wails/v3/pkg/events"
)
```

Feature packages include updater/providers, notifications, dock, and mobile/platform packages. Inspect the target module:

```bash
go doc github.com/wailsapp/wails/v3/pkg/application
go doc github.com/wailsapp/wails/v3/pkg/application.App
go list -m github.com/wailsapp/wails/v3
wails3 <command> --help
```

## Application

```go
app := application.New(application.Options{...})
err := app.Run()
app.Quit()
config := app.Config()

app.RegisterService(application.NewService(service))
```

Application options own name/description, services, assets, platform options, lifecycle callbacks, panic/raw-message handlers, single-instance/server/updater configuration, and other cross-cutting setup. Prefer declaring services in `Options.Services`; late `RegisterService` is useful when composition requires the app first.

Manager properties:

```text
app.Window       create/find/manage windows
app.Event        custom/application events
app.Menu         application menu
app.ContextMenu  named DOM context menus
app.KeyBinding   focused-app accelerators
app.GlobalShortcut system-wide accelerators
app.Dialog       native file/message dialogs
app.Browser      open external URL/file
app.Env          environment/theme/file manager
app.Screen       monitor information
app.Clipboard    text clipboard
app.SystemTray   tray icons/windows/menus
app.Autostart    login launch
app.Updater      update state machine
app.Logger       structured logging
```

## Windows

```go
window := app.Window.New()
window := app.Window.NewWithOptions(application.WebviewWindowOptions{...})
window, ok := app.Window.GetByName("main")
windows := app.Window.GetAll()
current := app.Window.Current()
app.Window.OnCreate(func(window application.Window) { ... })
```

Common `*application.WebviewWindow` operations:

```text
Show Hide Close Focus Center
SetTitle Name
SetSize Size SetMinSize SetMaxSize
SetPosition Position
Minimise UnMinimise Maximise UnMaximise
Fullscreen UnFullscreen ToggleFullscreen
IsMinimised IsMaximised IsFullscreen
SetURL SetHTML Reload Print
SetEnabled SetResizable SetAlwaysOnTop SetBackgroundColour
OnWindowEvent RegisterHook EmitEvent AttachModal
```

Many mutators are chainable. `OnWindowEvent` and `RegisterHook` return unsubscribe functions. Only hooks cancel supported events via `e.Cancel()`. `Close()` is the lifecycle operation; there is no `Destroy()`.

## Events

```go
cancelled := app.Event.Emit("name", data...)
off := app.Event.On("name", func(*application.CustomEvent) { ... })
off = app.Event.OnApplicationEvent(events.Common.ThemeChanged,
    func(*application.ApplicationEvent) { ... })

off = window.OnWindowEvent(events.Common.WindowFocus,
    func(*application.WindowEvent) { ... })
off = window.RegisterHook(events.Common.WindowClosing,
    func(e *application.WindowEvent) { e.Cancel() })
window.EmitEvent("name", data...)
```

Use `events.Common` for portable native events, platform namespaces only when necessary. Register application shutdown cleanup through lifecycle callbacks/methods rather than inventing a generic shutdown event.

Frontend events:

```ts
const off = Events.On(name, callback);
const offOnce = Events.Once(name, callback);
const offN = Events.OnMultiple(name, callback, max);
const cancelled = await Events.Emit(name, data);
Events.Off(name1, name2); // all listeners for names
Events.OffAll();
```

## Menus and tray

```go
menu := app.NewMenu()
item := menu.Add("Open")
submenu := menu.AddSubmenu("File")
menu.AddSeparator()
menu.AddCheckbox("Enabled", true)
menu.AddRadio("Choice", true)
menu.AddRole(application.EditMenu)

item.OnClick(func(*application.Context) { ... }).
    SetLabel("Open…").
    SetEnabled(true).
    SetChecked(false).
    SetAccelerator("CmdOrCtrl+O").
    SetTooltip("Open a document").
    SetHidden(false)

app.Menu.Set(menu)
window.SetMenu(menu)
```

Context menus use `app.ContextMenu.New()` and `app.ContextMenu.Add(name, *ContextMenu)`. Tray uses `app.SystemTray.New()`, then `SetIcon`, `SetMenu`, `SetTooltip`, `AttachWindow`, `OnClick`, and visibility/cleanup methods documented by the installed API.

## Dialogs

```go
path, err := app.Dialog.OpenFile().
    SetTitle("Open").AddFilter("Text", "*.txt").
    SetDirectory(dir).AttachToWindow(window).
    PromptForSingleSelection()

paths, err := app.Dialog.OpenFile().PromptForMultipleSelection()
path, err = app.Dialog.SaveFile().SetFilename("file.txt").PromptForSingleSelection()

dialog := app.Dialog.Question().SetTitle("Confirm").SetMessage("Continue?")
dialog.AddButton("Cancel").SetAsCancel()
dialog.AddButton("Continue").SetAsDefault().OnClick(action)
dialog.Show()

app.Dialog.Info()
app.Dialog.Warning()
app.Dialog.Error()
```

Directory selection is an open dialog configured with `CanChooseDirectories(true)` and `CanChooseFiles(false)`.

## Frontend runtime

```ts
import {
  Application, Browser, Clipboard, Dialogs, Events,
  Screens, System, Window
} from "@wailsio/runtime";
```

- `Window` targets the current window; `Window.Get(name)` selects another. It exposes show/hide/close, geometry/state, title/content/zoom/print/focus/screen operations.
- `Dialogs` exposes info/error/warning/question/open/save functions with option objects.
- `Clipboard.SetText`/`Text`, `Browser.OpenURL`, screen lookup, and application show/hide/quit mirror native managers.
- `System.invoke` sends raw messages and requires `RawMessageHandler`; prefer generated bindings.
- WML attributes provide simple declarative window/application/browser actions; avoid them when custom state/error handling is required.

## CLI groups

```text
init, dev, build, package, task, doctor, version
generate bindings|icons|build-assets|runtime|constants|syso|...
update cli|build-assets
setup, setup signing, setup entitlements
sign, tool sign|package|lipo|capabilities|...
updater genkey|manifest|verify|sign
service init
ios ...
```

Build/package/sign commands delegate heavily to project Taskfiles. Inspect `wails3 task --list` and command help; do not assume v2 flags or `build/bin` output.

## Stability

Desktop beta APIs aim for compatibility but defects and announced corrections may land before 3.0. Mobile and explicitly experimental features have weaker guarantees. Keep version checks close to code that depends on beta-only methods, and cite upstream source/commit in upgrade reviews.

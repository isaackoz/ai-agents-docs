# Menus, System Tray, and Keyboard

Use this reference for native application/context/tray menus, menu state, in-app accelerators, and system-wide shortcuts.

Sources: [application menus](https://v3.wails.io/features/menus/application/), [context menus](https://v3.wails.io/features/menus/context/), [tray menus](https://v3.wails.io/features/menus/systray/), [menu reference](https://v3.wails.io/features/menus/reference/), [menus guide](https://v3.wails.io/guides/menus/), [Menu API](https://v3.wails.io/reference/menu/), [key bindings](https://v3.wails.io/features/keyboard/shortcuts/), [global shortcuts](https://v3.wails.io/features/keyboard/global-shortcuts/).

Contents: [Application](#application-menu) · [Context](#context-menus) · [Tray](#system-tray) · [Key bindings](#in-app-key-bindings) · [Global shortcuts](#global-shortcuts) · [Failures](#failure-checklist)

## Application menu

```go
menu := app.NewMenu()
if runtime.GOOS == "darwin" {
    menu.AddRole(application.AppMenu)
}

fileMenu := menu.AddSubmenu("File")
fileMenu.Add("Open…").
    SetAccelerator("CmdOrCtrl+O").
    OnClick(func(ctx *application.Context) { openFile() })
fileMenu.AddSeparator()
fileMenu.Add("Quit").OnClick(func(ctx *application.Context) { app.Quit() })

menu.AddRole(application.EditMenu)
menu.AddRole(application.WindowMenu)
app.Menu.Set(menu)
```

Both `app.NewMenu()` and `app.Menu.New()` are valid in the pinned beta; the former delegates to the latter. Menus contain regular items, checkboxes, radio items/groups, separators, submenus, and role-based native structures. Items support click handlers and setters for label, enabled, checked, accelerator, tooltip, and hidden state.

Role menus supply OS conventions. On macOS add the App menu and standard roles; the app menu lives in the global menu bar. Windows/Linux normally attach menus to windows, while `app.Menu.Set` defines the application menu. A window can override it with `window.SetMenu` and `UseApplicationMenu` behavior.

`AddRole` may return the receiver rather than the inserted role submenu. When extending a role, find the inserted item by role and call `GetSubmenu()` instead of assuming the return value is that submenu.

Keep references to dynamic items and update them through their setters. Rebuild/reapply a menu when native state does not update automatically. Use `CmdOrCtrl` for cross-platform accelerators and respect OS-reserved conventions.

## Context menus

```go
contextMenu := app.ContextMenu.New()
contextMenu.Add("Open").OnClick(handleOpen)
contextMenu.Add("Delete").OnClick(func(ctx *application.Context) {
    id := ctx.ContextMenuData()
    // Validate id before acting.
})
app.ContextMenu.Add("file-menu", contextMenu)
```

Register a `*ContextMenu` under a unique name, then associate it with frontend elements using the documented Wails context-menu CSS custom property/data convention. Context data crosses from the DOM to the Go callback; treat it as untrusted input. Configure the default browser context menu as hidden, shown, or automatic depending on whether text fields still need standard edit actions.

There is no `app.RegisterContextMenu`; use `app.ContextMenu.Add(name, menu)`. Do not pass a normal `*Menu` where `*ContextMenu` is required.

## System tray

```go
tray := app.SystemTray.New()
tray.SetIcon(iconBytes)
tray.SetTooltip("My App")

trayMenu := app.NewMenu()
trayMenu.Add("Show").OnClick(func(ctx *application.Context) {
    mainWindow.Show().Focus()
})
trayMenu.Add("Quit").OnClick(func(ctx *application.Context) { app.Quit() })
tray.SetMenu(trayMenu)
tray.AttachWindow(mainWindow)
```

Keep the tray object alive for the application lifetime. Use template icons on macOS where appropriate. `AttachWindow` can supply default show/hide behavior; explicit `OnClick`/`OnRightClick` handlers replace corresponding defaults. Update icon/menu/status through the tray setters and remove/cleanup the tray during shutdown if the API requires it.

Tray-only apps need deliberate lifecycle policy: hiding/closing the main window should not unexpectedly quit, and the menu must always expose Quit. Validate icon formats and sizes on all target OSes.

## In-app key bindings

`app.KeyBinding` fires while an application window is focused:

```go
app.KeyBinding.Add("CmdOrCtrl+S", func(window application.Window) {
    saveActiveDocument(window)
})
app.KeyBinding.Add("F11", func(window application.Window) {
    // Toggle state using the concrete/runtime window API available here.
})

app.KeyBinding.Remove("CmdOrCtrl+S")
bindings := app.KeyBinding.GetAll()
```

Register shortcuts once, use active-window context rather than a stale pointer, and remove temporary mode-specific bindings. Avoid duplicating the same action through both a menu accelerator and an independent handler unless their interaction is understood.

## Global shortcuts

`app.GlobalShortcut` fires even when the app is unfocused:

```go
if err := app.GlobalShortcut.Register("CmdOrCtrl+Shift+G", func() {
    mainWindow.Show().Focus()
}); err != nil {
    app.Logger.Error("global shortcut unavailable", "error", err)
}
defer app.GlobalShortcut.Unregister("CmdOrCtrl+Shift+G")
```

Callbacks run on their own goroutine. Marshal native UI work as required by the relevant API. Always handle registration errors: another app/OS may own the shortcut. Registering an equivalent accelerator twice in one Wails app returns an error and preserves the first registration. On Wayland, the desktop portal/user may choose the final accelerator even when a preferred trigger is supplied.

## Failure checklist

- Item does nothing: retain menu/tray ownership, ensure the menu is applied, and verify the item is enabled/visible.
- Accelerator fails: normalize modifier spelling, use `CmdOrCtrl`, check focus and OS reservations.
- Context menu absent: register the exact name used by the frontend and check default-menu policy.
- Context action targets wrong object: pass a stable identifier and validate it in Go, not a mutable label/index.
- Tray icon missing: verify nonempty supported icon bytes and that the tray object is retained.
- Global shortcut conflicts: show feedback/fallback, then unregister before replacing the callback.

# System Integrations

Use this reference for autostart, external browser/file opening, clipboard text, environment and theme information, screens, notifications, and dock/taskbar state.

Sources: [autostart](https://v3.wails.io/features/autostart/basics/), [browser](https://v3.wails.io/features/browser/integration/), [clipboard](https://v3.wails.io/features/clipboard/basics/), [environment](https://v3.wails.io/features/environment/info/), [screens](https://v3.wails.io/features/screens/info/), [notifications](https://v3.wails.io/features/notifications/overview/), [dock/taskbar](https://v3.wails.io/features/platform/dock/).

Contents: [Autostart](#autostart) · [Browser](#browser-and-file-manager) · [Clipboard](#clipboard) · [Environment/screens](#environment-theme-and-screens) · [Notifications](#notifications-service) · [Dock](#dock-and-taskbar-service) · [Checklist](#capability-checklist)

## Autostart

```go
if enabledByUser {
    if err := app.Autostart.Enable(); err != nil { return err }
} else {
    if err := app.Autostart.Disable(); err != nil { return err }
}

enabled, err := app.Autostart.IsEnabled()
status, err := app.Autostart.Status()
```

`Enable` is idempotent and refreshes registration. `EnableWithOptions` supplies identifier/display options. `Status` includes whether enabled, the native registration path, and strategy (macOS service/LaunchAgent, Windows Run registry, Linux XDG autostart). Registrations match the resolved executable path so package-manager symlinks and identifier changes are handled; moving a portable executable can orphan an old entry. Autostart should always reflect an explicit user preference and use a stable installed path.

## Browser and file manager

```go
if err := app.Browser.OpenURL("https://docs.example.com"); err != nil { /* report */ }
if err := app.Browser.OpenFile(reportPath); err != nil { /* report */ }

if err := app.Env.OpenFileManager(reportPath, true); err != nil { /* reveal */ }
```

Allow only intended schemes/hosts for frontend-controlled URLs. Validate/canonicalize file paths, ensure generated files exist, and avoid opening executable or attacker-controlled content. `Browser.OpenFile` delegates to the OS default application; `Env.OpenFileManager(path, selectFile)` opens/reveals in the native file manager.

## Clipboard

```go
if ok := app.Clipboard.SetText(text); !ok {
    return errors.New("clipboard write failed")
}

text, ok := app.Clipboard.Text()
if !ok {
    return "", errors.New("clipboard does not contain readable text")
}
```

The documented manager handles text. Prefer it when Go needs clipboard access or browser clipboard permissions are unreliable. Treat pasted text as untrusted and cap its size. Do not poll the clipboard continuously without a clear feature and lifecycle cleanup. Rich formats are not part of the documented basic API.

## Environment, theme, and screens

```go
info := app.Env.Info()
dark := app.Env.IsDarkMode()
screens := app.Screen.GetAll()
primary := app.Screen.GetPrimary()
```

Environment information includes OS, architecture, debug status, and platform details. Use it for capability/UI branches, not as an authorization signal. Subscribe to the common theme-changed event rather than polling `IsDarkMode`.

Screen manager operations include all, primary, current/window-related, and ID lookup. Screen data includes bounds/work area, scale factor, and primary/current markers. Position windows using logical coordinates and work areas; stored geometry may be invalid after unplugging/rearranging monitors. Clamp restored windows into a current work area and respond to display changes.

## Notifications service

Notifications are a separately constructed service, not `app.Notification`:

```go
notifier := notifications.New()
app := application.New(application.Options{
    Services: []application.Service{
        application.NewService(notifier),
    },
})

authorized, err := notifier.CheckNotificationAuthorization()
if err == nil && !authorized {
    authorized, err = notifier.RequestNotificationAuthorization()
}

err = notifier.SendNotification(notifications.NotificationOptions{
    ID:       "sync-complete",
    Title:    "Sync complete",
    Body:     "All files are up to date.",
    ThreadID: "sync",
})
```

Register categories before sending interactive actions, then handle results with `OnNotificationResponse`. Options cover ID/title/body, metadata, sound, attachments, grouping/thread ID, interruption level, and scheduled delivery. Updating reuses an ID, but Windows beta behavior may redeliver rather than replace in place.

Platform requirements:

- macOS requires notification authorization; critical interruption requires OS support and entitlement. Bundled sounds/attachments must be packaged correctly.
- Windows supports action/taskbar integration with some update/removal differences.
- Linux requires an `org.freedesktop.Notifications` D-Bus daemon; handle its absence as a normal capability failure.

Do not request permission at first launch without context. Check every send error and provide an in-app fallback for important information.

## Dock and taskbar service

Dock is also a separately constructed service:

```go
dockService := dock.New()
app := application.New(application.Options{
    Services: []application.Service{
        application.NewService(dockService),
    },
})

_ = dockService.SetBadge("3")
_ = dockService.RemoveBadge()
```

macOS supports hiding/showing the dock icon and native badges. Windows renders configurable overlay badges via `BadgeOptions`. Linux does not support the documented dock visibility/badge functionality. Keep badge text short and clear it when state resolves. If hiding the macOS icon, provide tray/menu/shortcut access and an obvious Quit path.

## Capability checklist

- Record user preference before autostart or notification permission changes.
- Return/report native integration errors instead of assuming availability.
- Keep platform fallbacks for notifications, badges, and global UI features.
- Validate URLs, paths, clipboard input, notification metadata, and screen IDs.
- Keep services/tray/event subscriptions alive for the required lifetime and clean them up on shutdown.

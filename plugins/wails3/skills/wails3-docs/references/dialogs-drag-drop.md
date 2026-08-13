# Dialogs and Drag-and-Drop

Use this reference for native file/message dialogs, custom window-based dialogs, and internal or operating-system file drag-and-drop.

Sources: [dialog overview](https://v3.wails.io/features/dialogs/overview/), [file dialogs](https://v3.wails.io/features/dialogs/file/), [message dialogs](https://v3.wails.io/features/dialogs/message/), [custom dialogs](https://v3.wails.io/features/dialogs/custom/), [Dialogs API](https://v3.wails.io/reference/dialogs/), [file drop](https://v3.wails.io/features/drag-and-drop/files/), [HTML drag-and-drop](https://v3.wails.io/features/drag-and-drop/html/).

Contents: [Files](#native-file-dialogs) · [Messages](#native-messages-and-questions) · [Custom dialogs](#custom-dialogs) · [File drop](#operating-system-file-drop) · [HTML drag](#html-drag-and-drop) · [Failures](#failure-checklist)

## Native file dialogs

```go
path, err := app.Dialog.OpenFile().
    SetTitle("Open image").
    AddFilter("Images", "*.png;*.jpg;*.jpeg").
    SetDirectory(lastDirectory).
    AttachToWindow(mainWindow).
    PromptForSingleSelection()
if err != nil {
    return err
}
if path == "" {
    return nil // user cancelled
}
```

Use `PromptForMultipleSelection()` for multiple paths. Configure an open dialog with `CanChooseDirectories(true)` and `CanChooseFiles(false)` to select a folder; there is no separate `SelectFolderDialog`.

Save:

```go
saveDialog := app.Dialog.SaveFileWithOptions(&application.SaveFileDialogOptions{
    Title: "Export",
})
path, err := saveDialog.
    SetFilename("report.pdf").
    AddFilter("PDF", "*.pdf").
    AttachToWindow(mainWindow).
    PromptForSingleSelection()
```

In the pinned source, save-dialog titles are set through `SaveFileDialogOptions`; unlike the open-file builder, `SaveFileDialogStruct` has no chainable `SetTitle` method. Verify this when upgrading because some beta documentation still shows one.

Treat cancellation as normal. Validate the returned path, selected file type, permissions, overwrite policy, and any path containment constraints in Go. Filters guide the native picker; they do not validate content.

## Native messages and questions

```go
app.Dialog.Info().
    SetTitle("Saved").
    SetMessage("The document was saved.").
    AttachToWindow(mainWindow).
    Show()

question := app.Dialog.Question().
    SetTitle("Discard changes?").
    SetMessage("Unsaved changes will be lost.").
    AttachToWindow(mainWindow)

question.AddButton("Cancel").SetAsCancel()
question.AddButton("Discard").OnClick(discard)
question.Show()
```

Managers also create `Warning()` and `Error()` builders. Use explicit default/cancel buttons, concise user-facing text, and window attachment for correct modality/focus. Do not display raw sensitive diagnostic errors; log detail and show an actionable message.

Native dialog visual order, icons, modality, and button conventions differ by OS. Test destructive/default button behavior on each target.

## Custom dialogs

Build a custom dialog as another Wails window when native controls cannot express the UI:

- Give it a unique name and fixed/minimum size.
- Use a dedicated route or HTML content.
- Pass initial data through a service/event after runtime readiness rather than interpolating untrusted HTML.
- Use `parent.AttachModal(dialog)` only where platform support matches requirements; otherwise emulate app-level modality by disabling/overlaying the parent and restoring it reliably.
- Return results through a bound service or targeted event, close the window, and remove references/listeners.
- Implement focus trapping, Escape/cancel, accessible labels, keyboard navigation, and restoration of parent focus.

For progress dialogs, keep work in a cancellable Go operation and update the UI with events or a stream. Do not block the UI/event-loop callback.

## Operating-system file drop

External file drop is disabled by default:

```go
window := app.Window.NewWithOptions(application.WebviewWindowOptions{
    EnableFileDrop: true,
})

off := window.OnWindowEvent(events.Common.WindowFilesDropped,
    func(event *application.WindowEvent) {
        paths := event.Context().DroppedFiles()
        target := event.Context().DropTargetDetails()
        validateAndImport(paths, target)
    })
_ = off
```

Mark frontend drop zones with the documented Wails drop-target attribute so the native event includes useful target context. Full-window zones are valid. The event contains full local paths, which are sensitive input: canonicalize, validate extensions/content/size, reject directories or symlinks when inappropriate, and avoid automatic execution.

When file drop is off, Wails blocks external files from navigating the webview. When enabled, Wails handles external files while ordinary HTML drag events can still handle internal data.

## HTML drag-and-drop

Use standard HTML `draggable`, `dragstart`, `dragover`, and `drop`, with `dataTransfer` for stable IDs. Distinguish internal drags from OS files:

```ts
dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  if (event.dataTransfer?.types.includes("Files")) return;
  const itemID = event.dataTransfer?.getData("text/plain");
  if (itemID) moveItem(itemID);
});
```

Do not put privileged data or commands in `dataTransfer`; it is frontend-controlled. Use it to identify a domain object, then validate and execute privileged work through Go.

## Failure checklist

- Empty path with no error: likely user cancellation; do not report it as failure.
- Folder picker shows files: set both directory and file-selection options.
- Dialog appears behind the app: attach it to the correct live window.
- File drop event absent: enable it at window creation and mark a valid drop zone.
- Internal reorder triggers import: ignore `dataTransfer.types` containing `Files` in HTML handlers.
- Modal parent remains disabled: centralize cleanup for success, cancel, close, and error paths.

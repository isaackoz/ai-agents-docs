# Events, Streams, and Low-Level Transport

Use this reference for pub/sub communication, application/window lifecycle events, typed events, continuous byte traffic, raw messages, and custom transport decisions.

Sources: [event system](https://v3.wails.io/features/events/system/), [events guide](https://v3.wails.io/guides/events-reference/), [Events API](https://v3.wails.io/reference/events/), [streams](https://v3.wails.io/guides/streams/), [WebSocket migration](https://v3.wails.io/guides/streams-from-websockets/), [stream internals](https://v3.wails.io/guides/advanced/streams-internals/), [raw messages](https://v3.wails.io/guides/raw-messages/), [custom transport](https://v3.wails.io/guides/custom-transport/).

Contents: [Choose](#choose-the-mechanism) · [Events](#custom-events) · [Native events](#built-in-events-and-hooks) · [Streams](#streams) · [WebSocket migration](#migrate-a-local-websocket-workaround) · [Raw messages](#raw-messages) · [Transport](#custom-transport)

## Choose the mechanism

| Need | Mechanism |
|---|---|
| Request with result/error | Generated service binding |
| Broadcast notification, state invalidation, lifecycle signal | Event |
| Window-specific notification | `window.EmitEvent` |
| Cancellable native window action | `RegisterHook`, not a custom event |
| Continuous bidirectional bytes | Stream |
| Performance-critical custom string message | Raw message, with origin validation |
| Replace bridge transport itself | Custom transport; advanced and rarely necessary |

## Custom events

Go:

```go
app.Event.Emit("orders:updated", orderID)

unsubscribe := app.Event.On("ui:refresh-requested", func(e *application.CustomEvent) {
    // e.Data is any; validate and decode the expected payload.
})
defer unsubscribe()

window.EmitEvent("document:loaded", document)
```

Frontend:

```ts
import { Events } from "@wailsio/runtime";

const off = Events.On("orders:updated", (event) => {
  // Consume payload according to generated/runtime event shape.
});

Events.Emit("ui:refresh-requested", { force: false });
off();
```

`Events.On` returns the unsubscribe for one listener. `Events.Off(name, ...)` removes all listeners for the supplied names and does not accept a callback. `Events.OffAll()` removes every frontend listener. Use `Once` for one delivery and `OnMultiple` for a bounded count.

In Go, `CustomEvent.Data` is `any`: emitting no payload sets it to `nil`, one argument stores that value directly, and multiple Go arguments store an `[]any`. Frontend `Events.Emit(name, data)` accepts one payload value and listeners read it from `event.data`; pass an array/object explicitly when the payload has several fields.

Namespace custom names (`feature:entity:action`) to avoid collisions. Always clean up subscriptions when components/windows are disposed. Debounce or batch resize, telemetry, and other high-frequency events.

## Built-in events and hooks

Import native identifiers from the Wails event packages rather than spelling strings in Go:

```go
app.Event.OnApplicationEvent(events.Common.ThemeChanged,
    func(e *application.ApplicationEvent) { /* ... */ })

window.OnWindowEvent(events.Common.WindowDidResize,
    func(e *application.WindowEvent) { /* observe */ })

window.RegisterHook(events.Common.WindowClosing,
    func(e *application.WindowEvent) {
        if hasUnsavedChanges() {
            e.Cancel()
        }
    })
```

Common application events cover startup, theme changes, sleep/wake, and opening files. Window events cover runtime readiness, focus, move/resize, minimize/maximize/fullscreen, file drop, and closing. Platform packages add OS-specific events. Only hooks can cancel supported native actions; passive listeners cannot.

Typed custom events can be registered in Go and emitted into generated TypeScript through the Wails Vite event plugin/generator. Prefer typed events for shared payload contracts and strict generation in larger codebases.

## Streams

Streams provide WebSocket-shaped bidirectional byte frames without a listening TCP port in desktop builds.

```go
app.HandleStream("telemetry", func(c *application.StreamConn) {
    defer c.Close()
    for {
        payload, err := c.Receive()
        if err != nil {
            return
        }
        if err := c.Send(payload); err != nil {
            return
        }
    }
})
```

```ts
import { Stream, JSONStream } from "@wailsio/runtime";

const stream = Stream("telemetry");
stream.binaryType = "arraybuffer";
stream.onmessage = (event) => consume(new Uint8Array(event.data));
stream.onopen = () => stream.send(new TextEncoder().encode("start"));

const json = JSONStream("structured");
json.onmessage = (event) => consumeObject(event.data);
```

Key behavior:

- `Stream(name)` returns synchronously in `CONNECTING` state.
- Frames are bytes; received `event.data` is an `ArrayBuffer`, never a WebSocket text string. Use `JSONStream` or explicit encode/decode for objects/text.
- There is no URL, query string, subprotocol, automatic reconnect, or built-in broadcast registry.
- Go `Send` blocks under bounded backpressure; `TrySend` can drop rather than wait. Frontend `send()` buffers synchronously and exposes `bufferedAmount`.
- Each stream connection is window/session scoped. Close it and stop handler goroutines.
- Desktop transport is origin-bound without a TCP listener. A `-tags server` build maps the same API to real same-origin WebSockets; only add trusted `ServerOptions.WebSocketOriginPatterns` when needed.
- Streams do not work for initial-HTML windows whose origin is `null`.

Use a service call for isolated operations and events for fan-out signals. Streams are appropriate for terminals, media chunks, telemetry, broker proxies, and protocols that naturally use frames.

## Migrate a local WebSocket workaround

1. Replace upgrader/listener/mux registration with `app.HandleStream(name, handler)`.
2. Remove the local port, token, CORS, and origin-check code used solely for the loopback WebSocket.
3. Replace `new WebSocket(url)` with `Stream(name)` or `JSONStream(name)`.
4. Move connection parameters into an initial frame or a bound setup method; streams have no URL/query.
5. Decode incoming `ArrayBuffer` values; sending strings/typed arrays remains WebSocket-like but receiving differs.
6. Keep or implement reconnect and broadcast registries explicitly.
7. Keep direct broker WebSockets only when the frontend intentionally connects to an external broker; otherwise proxy credentials/protocol through a named stream.

## Raw messages

`application.Options.RawMessageHandler` receives the window, string message, and origin information. Use it only when generated binding overhead or the required wire shape justifies losing type generation.

Always validate `Origin`, `TopOrigin` where available, and `IsMainFrame` before parsing or mutating state. Allow only exact trusted application origins, reject unknown actions/fields, enforce message size limits, and reply to the originating window with `window.EmitEvent` unless broadcast is intentional.

## Custom transport

A custom transport replaces bridge delivery while retaining binding/event semantics. It requires a Go transport implementation, application configuration, and compatible frontend runtime transport. This is infrastructure work: define framing, request correlation, cancellation, origin/authentication, error serialization, reconnection, and backpressure. Prefer the built-in bridge, streams, asset-server middleware, or server build unless a deployment constraint proves they cannot work.

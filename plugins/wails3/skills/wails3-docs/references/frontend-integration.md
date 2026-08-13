# Frontend, Routing, HTTP Integration, and Server Mode

Use this reference for non-default frontend frameworks, runtime APIs, routing, Gin/HTTP services, server builds, and transport selection.

Sources: [frontend frameworks](https://v3.wails.io/guides/dev/frontend-frameworks/), [project structure](https://v3.wails.io/guides/dev/project-structure/), [routing](https://v3.wails.io/guides/routing/), [frontend runtime](https://v3.wails.io/reference/frontend-runtime/), [Gin routing](https://v3.wails.io/guides/gin-routing/), [Gin services](https://v3.wails.io/guides/gin-services/), [custom transport](https://v3.wails.io/guides/custom-transport/), [server build](https://v3.wails.io/guides/server-build/).

Contents: [Frontend](#frontend-contract) · [Runtime](#frontend-runtime) · [Routing](#routing) · [HTTP/Gin](#when-to-add-httpgin) · [Server](#server-build) · [Transport](#custom-transport-decision) · [Failures](#common-failures)

## Frontend contract

Wails accepts any frontend that produces static assets. Standard templates assume:

- source and package scripts under `frontend/`;
- `frontend/package.json` has `dev` and `build` scripts;
- production output is `frontend/dist/`, matching the Go embed path;
- generated Go bindings live under `frontend/bindings/` by default;
- Vite binds the port from `WAILS_VITE_PORT` (default 9245) with `strictPort: true`;
- `@wailsio/runtime` supplies native runtime modules.

```ts
// vite.config.ts
import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  server: {
    host: "127.0.0.1",
    port: Number(process.env.WAILS_VITE_PORT) || 9245,
    strictPort: true,
  },
});
```

To replace the frontend, scaffold a static Vite app in `frontend/`, install `@wailsio/runtime`, preserve/update package scripts and Taskfile commands, configure the port/output/base, regenerate bindings, then test both `wails3 dev` and production `wails3 build`. Framework-specific SSR/server features must be disabled or adapted to static output for desktop embedding.

The runtime’s Vite plugin is optional unless typed custom event generation/HMR is used.

## Frontend runtime

Prefer tree-shakable imports:

```ts
import { Events, Window, Clipboard, Dialogs, Browser, Screens, Application } from "@wailsio/runtime";
```

Runtime modules expose current-window controls, named windows, events, clipboard, browser opening, screens, application show/hide/quit, native dialogs, raw `System.invoke`, streams, and WML declarative attributes. Generated service modules remain the interface for application business methods. Use raw invoke only with a configured, origin-validating handler.

Initialize/import the runtime before code that subscribes or calls native features. Keep event unsubscriptions. Verify exact method casing and return types from installed TypeScript definitions because beta APIs can change.

## Routing

Use hash routing (`#/settings`) for reliable embedded navigation: Vue web hash history, React `HashRouter`, Angular hash location, or a Svelte SPA hash router. Set Vite `base: "./"`. History-mode paths may request nonexistent embedded asset routes on reload/direct navigation unless custom asset middleware implements an SPA fallback. If choosing history routing, explicitly serve `index.html` for safe non-file routes while preserving assets and Wails endpoints.

Do not use a desktop route to represent privileged file paths or protocol input without validation. Route custom-protocol/file-open events through a typed navigation model.

## When to add HTTP/Gin

Do not add Gin merely so the Wails frontend can call Go; generated bindings are simpler and typed. Add an HTTP router when the app must expose or reuse actual HTTP endpoints, middleware, webhooks, downloads, or a browser/server deployment.

Two documented patterns:

1. Use a Gin engine as/middleware around the application asset handler. Preserve Wails runtime/binding routes and delegate only intended paths.
2. Implement `http.Handler` on a service and register it with `application.NewServiceWithOptions(..., application.ServiceOptions{Route: "/api"})` so its router is mounted under a scoped path.

For either pattern, separate frontend asset fallback from `/api`, validate/authenticate requests, limit body sizes, use Gin release mode in production, propagate context, and test routes with `httptest`. Same-origin does not eliminate CSRF/XSS/authorization concerns when remote/untrusted content can load.

Use Wails streams rather than a Gin WebSocket when the only client is the embedded frontend and no network listener is needed.

## Server build

The `server` build tag runs the same application as an HTTP server without native GUI dependencies:

```bash
wails3 task build:server
wails3 task run:server
# or: go build -tags server -o myapp-server .
```

```go
app := application.New(application.Options{
    Server: application.ServerOptions{
        Host: "127.0.0.1",
        Port: 8080,
        WebSocketOriginPatterns: []string{"app.example.com"},
    },
    Assets: application.AssetOptions{
        Handler: application.AssetFileServerFS(assets),
    },
})
```

Bindings operate through HTTP and Go-to-browser events/streams use real WebSockets. In the pinned source, window creation returns a non-nil `*WebviewWindow` backed by a no-op server implementation; it is not a native window, geometry/state values are placeholders, and unsupported operations may return errors. Older beta guide text says it returns `nil`, so capability-gate shared code with `application.System.IsServer()` instead of depending on either behavior. Native menus/dialogs/tray/window APIs are unavailable or no-op. Provide web equivalents or gate features.

Deployment rules:

- Bind externally (`0.0.0.0`) only in controlled container/server deployments; default to loopback for local tools.
- Terminate TLS, enforce authentication/authorization, request limits, timeouts, and secure headers.
- Keep WebSockets same-origin. Allow only required origins; avoid `WebSocketAllowAllOrigins`.
- Protect/limit any health endpoint and never expose debug/pprof accidentally.
- Use graceful SIGINT/SIGTERM shutdown and health/readiness semantics suitable for the orchestrator.
- Review Wails server environment variables; deployment overrides take precedence over code.

## Custom transport decision

A custom transport replaces bridge delivery in both Go and frontend. Before implementing one, document why generated fetch calls, service HTTP routes, streams, or server mode are insufficient. Then specify request IDs, framing, errors, cancellation, reconnection, authentication/origin, maximum sizes, ordering, backpressure, asset routing, and shutdown. Test compatibility with generated bindings/events rather than hand-calling internal endpoints.

## Common failures

- Dev server not found: honor `WAILS_VITE_PORT`, bind loopback, use `strictPort`, and check Taskfile command.
- Blank production route: use static output, relative base, hash routing, correct `dist` embed, and production asset handler.
- Runtime import works in dev only: install/bundle `@wailsio/runtime`; do not rely on an ungenerated `/wails/runtime.js` accidentally present in dev.
- API route captures assets/runtime: scope router middleware and pass unmatched requests to Wails.
- Server events fail cross-origin: use same origin or a narrow `WebSocketOriginPatterns` entry and configure TLS/proxy headers correctly.
- Native call in server mode has no effect or returns an unsupported error: capability-gate it and do not infer native capability from a non-nil window value.

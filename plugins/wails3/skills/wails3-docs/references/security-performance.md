# Security and Performance

Use this reference when a Wails boundary accepts frontend/external input, loads remote content, touches files/secrets/network, or needs measured responsiveness and resource improvements.

Sources: [security](https://v3.wails.io/guides/security/), [performance](https://v3.wails.io/guides/performance/), [bridge](https://v3.wails.io/concepts/bridge/), [binding best practices](https://v3.wails.io/features/bindings/best-practices/).

## Threat model

Generated bindings provide typed serialization, not trust. Inputs may originate from compromised frontend dependencies, XSS, loaded remote pages/iframes, clipboard, drag-and-drop, files, custom protocols, second-instance args, events, HTTP/server clients, or malicious update infrastructure.

For every privileged Go operation:

1. Define allowed input types, lengths, ranges, formats, and state transitions.
2. Authenticate/authorize when identities or privileges exist.
3. Canonicalize paths/URLs before policy checks; avoid string-prefix containment checks.
4. Apply operation-specific timeouts, cancellation, body/payload limits, and rate limits.
5. Return safe errors and log diagnostic context without secrets.
6. Test invalid, oversized, traversal, concurrent, and replay inputs.

## Files and URLs

Resolve a requested path against an allowed base using `filepath.Abs`/`EvalSymlinks` as required, then use `filepath.Rel` to prove it remains contained. A check for `".."` alone is insufficient. Open files with least privilege, reject unexpected symlinks/devices/types, enforce maximum sizes, and use atomic temp-write/rename patterns for durable updates.

Parse URLs with `net/url`; allowlist schemes and hosts. Never pass untrusted strings to a shell. Escape values for their output context—HTML escaping is different from URL, JavaScript, SQL, or command escaping. Avoid exposing local-file or privileged binding access to windows that load remote/untrusted content.

## Secrets and data protection

- Do not hardcode or commit private update/signing keys, API tokens, certificate passwords, encryption keys, or user credentials.
- Store passwords with an adaptive password hash, not reversible encryption or fast hashes.
- Use OS keychain/credential services for local secrets when practical.
- Use standard authenticated encryption with random nonces and a well-managed key for data that truly needs application-level encryption.
- Require HTTPS with normal certificate verification. Custom TLS transports must retain hostname and chain verification; do not ship insecure skip-verify settings.
- Redact secrets and sensitive user data from logs, events, crash reports, clipboard history, updater headers, and analytics.

## Window/runtime hardening

- Grant minimum per-window permissions and include required OS entitlements/usage descriptions.
- Prefer local bundled content. If remote content is required, isolate it from privileged services and validate navigations/origins.
- Keep raw message handlers origin- and frame-validated.
- Keep server WebSockets same-origin or narrowly allowlisted.
- Do not enable updater `AllowSimpleEventEmit` for untrusted content.
- Treat custom event names and payloads as input; do not map arbitrary names directly to privileged actions.
- Keep dependencies updated and use a restrictive content security policy compatible with the frontend where feasible.

## Performance process

Measure before changing architecture:

1. Reproduce a user-visible slow path with stable data.
2. Separate frontend render/network-like bridge time, Go work, native/webview behavior, and packaging/debug overhead.
3. Capture browser performance profiles, Go benchmarks/trace/pprof, allocation data, and event/stream rates.
4. Change one bottleneck and compare latency, throughput, memory, CPU, startup, and binary size.
5. Add a regression test/benchmark for critical paths.

## Bridge and event efficiency

- Batch related operations and paginate large collections.
- Avoid bridge calls in animation, pointer-move, scroll, and keystroke loops.
- Cache expensive stable results with explicit invalidation and bounded size.
- Emit progress at a human-useful rate, not for every byte/item.
- Debounce/coalesce resize/theme/state invalidations.
- Use streams for sustained framed traffic; respect backpressure and cancel inactive consumers.
- Protect singleton service state. Each binding call may run concurrently.
- Keep long I/O off UI/native callback paths, but do not spawn unbounded goroutines. Own cancellation and wait for shutdown.

## Frontend efficiency

Use production builds, tree-shakable runtime imports, route/component code splitting, optimized images/fonts, virtualized/paginated large lists, and derived state instead of duplicate copies. Clean event listeners, timers, observers, object URLs, and stream connections on component/window disposal. Profile before adding memoization or a state library.

## Go resource rules

- Pass contexts through I/O and set deadlines.
- Bound worker pools, queues, caches, retained event data, and stream frames.
- Close files, rows, bodies, streams, tickers, and native registrations.
- Reuse expensive connections, not arbitrary objects whose lifetime/ownership becomes unclear.
- Prefer simple allocations until profiles show a pool helps; `sync.Pool` is not a general cache.
- Run `go test -race` for concurrent service changes and inspect goroutine/heap growth across repeated open/close cycles.

## Release optimization

Wails Taskfiles generally strip symbols for production. Optimize frontend assets first, then inspect Go binary dependencies and build tags. UPX/obfuscation can break signing, trigger antivirus, complicate crash diagnostics, or yield small real gains; evaluate on final packaged targets. Never trade update verification, TLS validation, or input checks for speed.

## Review checklist

- Are every frontend/external input and origin validated in Go?
- Are privileged operations authorized and minimally exposed?
- Are paths, URLs, secrets, update keys, and logs handled safely?
- Are listeners, goroutines, streams, windows, and native registrations cleaned up?
- Are high-frequency calls batched/debounced and queues bounded?
- Is the change measured in production-like builds and tested on affected OS/webview versions?

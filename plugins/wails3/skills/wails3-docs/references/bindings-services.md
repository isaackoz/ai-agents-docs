# Bindings, Services, Models, and Enums

Use this reference to expose Go functionality, generate frontend clients, design bridge DTOs, handle errors, and customize generated bindings.

Sources: [method bindings](https://v3.wails.io/features/bindings/methods/), [services](https://v3.wails.io/features/bindings/services/), [models](https://v3.wails.io/features/bindings/models/), [enums](https://v3.wails.io/features/bindings/enums/), [advanced binding](https://v3.wails.io/features/bindings/advanced/), [best practices](https://v3.wails.io/features/bindings/best-practices/), [bridge](https://v3.wails.io/concepts/bridge/).

Contents: [Services](#define-and-register-a-service) · [Generation](#generate-bindings) · [Models](#model-design) · [Enums](#enums) · [Lifecycle](#lifecycle-and-service-options) · [Directives](#advanced-generation-directives) · [Checklist](#api-design-checklist) · [Failures](#common-failures)

## Define and register a service

```go
type CalculatorService struct {
    mu sync.RWMutex
}

func (s *CalculatorService) Divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

service := &CalculatorService{}
app := application.New(application.Options{
    Services: []application.Service{
        application.NewService(service),
    },
})
```

Only exported methods selected by the binding generator are callable. Services are singleton instances, so synchronize shared mutable state. Construct dependencies before registration; do not use a service locator when constructor injection is sufficient.

Methods commonly return nothing, one serializable value, `error`, or `(value, error)`. A Go error becomes a rejected JavaScript promise:

```ts
import { Divide } from "./bindings/example/calculatorservice";

try {
  const result = await Divide(10, 2);
} catch (error) {
  // Show a safe user-facing message; retain diagnostic context in Go logs.
}
```

Inspect generated imports in the actual project; package/module names determine paths and filenames.

## Generate bindings

```bash
wails3 generate bindings
wails3 generate bindings -ts
wails3 generate bindings -d frontend/bindings ./...
```

Generation can emit JavaScript or TypeScript, model classes/interfaces, index files, event constants, named calls, or a bundled runtime. Keep generation flags in the Taskfile so dev/build/CI agree. Never patch generated files.

Regenerate when:

- adding/removing/renaming a service or exported method;
- changing arguments, results, model fields, JSON tags, or enums;
- adding registered typed events;
- changing binding directives, package patterns, output flags, or runtime bundling.

## Model design

Use explicit transport structs with JSON tags:

```go
type UserDTO struct {
    ID          string     `json:"id"`
    DisplayName string     `json:"displayName"`
    Email       *string    `json:"email,omitempty"`
    CreatedAt   time.Time  `json:"createdAt"`
    Roles       []Role     `json:"roles"`
    Metadata    map[string]string `json:"metadata,omitempty"`
}
```

Supported shapes include primitives, structs, pointers, slices/arrays, maps with suitable keys, nested models, and common time values. Avoid channels, functions, complex numbers, unsafe pointers, cyclic graphs, and interface-heavy data without an explicit serializable representation.

Rules:

- Use pointers when null/absence is semantically distinct from a zero value.
- Do not expose database entities containing secrets or internal-only fields.
- Keep maps and arbitrary JSON for truly dynamic data; generated structs give better frontend types.
- Validate at the Go boundary even if TypeScript prevents ordinary mistakes.
- Paginate or stream large data rather than returning unbounded payloads.

## Enums

Define a named Go type plus a coherent const block. The generator can produce frontend enum values for supported string/integer underlying types:

```go
type Role string

const (
    RoleUnknown Role = "unknown"
    RoleAdmin   Role = "admin"
    RoleUser    Role = "user"
)
```

Give zero values explicit semantics because models may be default-constructed. Preserve enum wire values across releases. Comments can flow into generated documentation; use them to explain non-obvious values, not implementation history.

## Lifecycle and service options

Implement `ServiceStartup(ctx context.Context, options application.ServiceOptions) error` and `ServiceShutdown() error` for resources that need app lifetime management. Startup runs in registration order; a failure aborts startup and shuts down services already started. The context remains valid while the app runs and is cancelled immediately before shutdown. Shutdown runs in reverse registration order after user application shutdown hooks. Start cancellable work in startup, make shutdown idempotent, and avoid launching ownerless goroutines in a constructor.

Services may define a custom public name and HTTP routes/options. Use custom names only for intentional API compatibility. Use HTTP routes for integrations that actually speak HTTP; generated bindings remain the default frontend interface.

## Advanced generation directives

Wails binding directives can:

- inject custom code into generated output;
- include additional frontend files;
- mark types/methods internal or ignored;
- assign stable custom method IDs;
- choose names rather than numeric IDs;
- suppress index/event files or bundle the runtime.

Before adding a directive, inspect nearby working declarations and run `wails3 generate bindings -dry` or verbose generation if supported. Stable IDs matter for obfuscated builds; follow the obfuscation workflow rather than inventing IDs ad hoc.

## API design checklist

- Give each service one domain responsibility.
- Prefer `ListUsers(filter)` over several calls that fetch the same screen piecemeal.
- Pass context/cancellation where supported for I/O and long work.
- Return stable, actionable errors without sensitive details.
- Avoid high-frequency calls on animation/input loops; debounce, batch, event, or stream.
- Authenticate/authorize privileged operations in Go.
- Unit-test services and serialization-relevant models; mock dependencies, not generated bindings.
- Keep frontend cleanup around event subscriptions separate from one-shot method calls.

## Common failures

- Binding import missing: regenerate, check service registration/package pattern, then inspect output path.
- Method absent: it may be unexported, ignored by a directive, unsupported, or outside generation patterns.
- Stale TypeScript: clean/regenerate bindings and ensure Taskfiles do not target a different directory.
- Promise rejects with opaque text: wrap Go errors with operation context and map known domain failures in the frontend.
- Races or intermittent state: services are shared and calls are concurrent; add synchronization or redesign ownership.

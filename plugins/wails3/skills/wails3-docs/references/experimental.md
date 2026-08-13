# Experimental Features

These features are explicitly experimental in Wails v3 beta. Use them only when requested, isolate them behind configuration/build tags, pin versions, and provide a fallback.

Sources: [experimental overview](https://v3.wails.io/experimental/), [Wake](https://v3.wails.io/experimental/wake/), [LLM/MCP control](https://v3.wails.io/guides/mcp-service/). Upstream source for the overview is `experimental/index.mdx`.

## Wake

Wake is a Wails-aware experimental build runner for existing Taskfiles. It aims to improve incremental execution, structured output, and parallelism without replacing project tasks. Enable it using the documented Wails/Wake configuration or environment option, keep Taskfiles valid under the standard embedded Task runner, and rely on automatic/manual fallback when Wake fails.

Guidelines:

- Do not rewrite build logic solely for Wake.
- Keep layered local overrides uncommitted when they contain machine paths or developer preferences.
- Compare output/artifacts with `wails3 task` before adopting it in CI.
- Pin the Wails beta/commit because Wake behavior and environment variables can change.
- Report reproducible failures with the task graph and structured output.

## LLM control through MCP

The MCP service lets an external agent inspect and control a Wails app for testing. It is compiled/run with the documented `mcp` build tag and exposes tools for windows and DOM elements.

Use it as a development/test surface, never an unreviewed production remote-control interface:

1. Keep MCP builds separate from release builds.
2. Bind locally or to an explicitly protected transport.
3. Do not expose secrets or privileged application methods through selectable UI/actions.
4. Use stable element selectors/attributes so agent tests do not depend on text/visual position.
5. Confirm the intended window before acting in multi-window apps.
6. Reset test state and capture logs/screenshots/results for reproducibility.

The exact client connection configuration and available tools are beta-specific; read `wails3 <relevant-command> --help`, the current MCP guide, and the example app before wiring a client. If the feature is absent in the installed version, do not emulate it by opening an unauthenticated control port.

## Adoption checklist

- Is the feature explicitly requested and available in the pinned Wails version?
- Is it isolated from ordinary production paths?
- Is there a standard Task runner/manual testing fallback?
- Are authentication, network exposure, selector stability, and test data controlled?
- Can the feature be removed without redesigning application business logic?

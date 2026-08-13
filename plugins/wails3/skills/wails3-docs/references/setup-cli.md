# Setup, Projects, CLI, and Templates

Use this reference to install Wails v3, create or inspect a project, select a frontend template, and choose CLI commands. Prefer `wails3 <command> --help` over this snapshot for exact flags when the installed CLI differs.

Sources: [quick installation](https://v3.wails.io/quick-start/installation/), [installation](https://v3.wails.io/getting-started/installation/), [setup](https://v3.wails.io/getting-started/setup/), [first app](https://v3.wails.io/quick-start/first-app/), [first application](https://v3.wails.io/getting-started/your-first-app/), [next steps](https://v3.wails.io/quick-start/next-steps/), [why Wails](https://v3.wails.io/quick-start/why-wails/), [project structure](https://v3.wails.io/guides/dev/project-structure/), [CLI guide](https://v3.wails.io/guides/cli/), [CLI reference](https://v3.wails.io/reference/cli/), [custom templates](https://v3.wails.io/guides/advanced/custom-templates/).

Contents: [Install](#requirements-and-installation) · [Create](#create-and-run-a-project) · [Commands](#everyday-commands) · [Generation](#generation) · [Frontend/templates](#frontend-choice-and-custom-templates) · [Troubleshooting](#troubleshooting-setup)

## Requirements and installation

- Use Go 1.25+ for the beta.8 desktop contract.
- Windows amd64/arm64 requires WebView2, normally already installed.
- macOS requires Xcode Command Line Tools: `xcode-select --install`.
- Linux defaults to GTK4 + WebKitGTK 6.0. Ubuntu 24.04+/Debian 13+ satisfy that baseline. Older supported distributions with GTK3 + WebKit2GTK 4.1 require `-tags gtk3`; this compatibility path ends in v3.1.
- A Node package manager is optional to Wails but required by most frontend templates.

```bash
go install github.com/wailsapp/wails/v3/cmd/wails3@latest
wails3 doctor
```

`wails3 setup` is an experimental browser-based wizard for dependency checks, defaults, Docker cross-build setup, and signing. It writes `~/.config/wails/config.yaml`. Fall back to manual installation and `wails3 doctor` if it fails.

## Create and run a project

```bash
wails3 init -n myapp -t vanilla
cd myapp
wails3 dev
wails3 build
```

Use `wails3 init -l` to list built-in templates. Common names include `vanilla`, `vanilla-js`, `react`, `react-js`, `vue`, and `svelte`. Relevant `init` flags:

| Flag | Meaning |
|---|---|
| `-n` | Project name |
| `-t` | Built-in template name, local path, or remote template URL |
| `-d` | Destination, default `.` |
| `-mod` | Go module path |
| `-git` | Initialize Git with this remote; can also derive the module path |
| `-l` | List templates |
| `-skipgomodtidy` | Skip the initial `go mod tidy` |

Typical generated shape:

```text
main.go                 application construction and windows
<service>.go            bound Go service
frontend/               Vite application and generated bindings
build/config.yml        product and platform build metadata
build/                  platform assets and Taskfile includes
Taskfile.yml            dev/build/package orchestration
go.mod
```

`wails3 dev`, `build`, and `package` invoke project Taskfile tasks. Inspect them before replacing commands or assuming output layout. Binaries and packages normally land under `bin/`, not `build/bin/`.

## Everyday commands

| Command | Purpose |
|---|---|
| `wails3 dev` | Run with frontend hot reload and Go rebuild/relaunch |
| `wails3 build` | Run the Taskfile build for the host platform |
| `wails3 build -tags gtk3` | Build with legacy Linux GTK3/WebKit2GTK 4.1 |
| `wails3 build -tags server` | Build the headless server variant |
| `wails3 package` | Run the platform package task |
| `wails3 task --list` | Show project tasks |
| `wails3 task <name> KEY=value` | Run a task with variables |
| `wails3 doctor` | Diagnose toolchain and native dependencies |
| `wails3 version` | Print CLI version |
| `wails3 update cli` | Update the CLI |
| `wails3 update build-assets` | Refresh generated build support files |

Useful `dev` flags include `-config`, `-port`, and `-s` (HTTPS). `build` accepts Task variables and `-tags`. Use `wails3 build --help` before relying on newer options such as obfuscation.

## Generation

Run binding generation after changing exported service methods, referenced models, registered events, or generation directives:

```bash
wails3 generate bindings
wails3 generate bindings -ts
wails3 generate bindings -d frontend/bindings ./...
```

Important binding flags include `-ts`, `-i` (interfaces), `-d`, `-models`, `-index`, `-noindex`, `-noevents`, `-names`, `-b` (bundle runtime), `-clean`, and `-dry`. Never edit its output.

Other generators:

- `wails3 generate icons -input icon.png`
- `wails3 generate build-assets`
- `wails3 generate runtime`
- `wails3 generate constants`
- `wails3 generate syso` and `webview2bootstrapper` for Windows
- `wails3 generate .desktop` and `appimage` for Linux
- `wails3 generate template` to scaffold a custom template

## Frontend choice and custom templates

For a framework without a built-in template, create its Vite project under `frontend/`, ensure its production build output matches the asset path used by the Go embed/application, and update Taskfile install/build/dev commands. Wails does not require React, Vue, Svelte, or npm specifically.

A Wails template is a normal project skeleton with template metadata and substitution tokens. Generate a starting template with `wails3 generate template`, then test it with `wails3 init -t /absolute/or/relative/template/path`. Remote templates execute project setup content, so use trusted repositories and do not suppress the remote-template warning without review.

## Troubleshooting setup

- `wails3: command not found`: add `$(go env GOPATH)/bin` (usually `~/go/bin`) to `PATH`, then restart the shell.
- CLI/module mismatch: inspect `wails3 version`, `go.mod`, and any `replace` directive. A CLI built from a Wails checkout may generate projects pinned to that checkout.
- First `dev` is slow: it installs frontend packages, generates bindings, and populates Go caches.
- Linux native compile failure: run `wails3 doctor`; verify GTK/WebKit development packages match the selected `gtk3` tag.
- Unexpected build behavior: inspect `Taskfile.yml`, included `build/Taskfile*.yml`, and `build/config.yml`; CLI lifecycle commands are wrappers.

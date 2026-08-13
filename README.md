# ai-agents-docs

A general repository for Codex agent instructions, skills, plugins, and templates.

## Codex Plugins

This repo exposes the following Codex plugins through the repo marketplace at `.agents/plugins/marketplace.json`:

- `isaac-stack`: Isaac's reusable development stack.
- `wails3`: LLM-friendly Wails 3 beta documentation and implementation guidance.

To install from this GitHub repo:

```bash
codex plugin marketplace add <owner>/<repo> --ref main
```

Then open Codex from inside a project and install or enable the desired plugin from the plugin directory.

To update:

```bash
git pull
codex plugin marketplace upgrade
```

Restart Codex or start a new thread if updated skills are not picked up.

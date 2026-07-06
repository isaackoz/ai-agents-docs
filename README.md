# ai-agents-docs

A general repository for Codex agent instructions, skills, plugins, and templates.

## Isaac Stack Plugin

This repo exposes the `isaac-stack` Codex plugin through the repo marketplace at `.agents/plugins/marketplace.json`.

To install from this GitHub repo:

```bash
codex plugin marketplace add <owner>/<repo> --ref main
```

Then open Codex from inside a project and install or enable the `Isaac Stack` plugin from the plugin directory.

To update:

```bash
git pull
codex plugin marketplace upgrade
```

Restart Codex or start a new thread if updated skills are not picked up.

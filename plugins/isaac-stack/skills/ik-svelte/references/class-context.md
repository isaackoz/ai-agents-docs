# Class Context Pattern

Use this reference when shared state crosses component boundaries or a large Svelte page needs to be split into context-backed child components.

The file containing rune-based class state must use a `.svelte.ts` extension. A plain `.ts` extension will not work for Svelte runes.

```ts
import { getContext, setContext } from 'svelte';
import { SvelteDate, SvelteMap, SvelteSet, SvelteURL } from 'svelte/reactivity';

type InitialContextState = {
	initialName?: string;
};

export class FeatureContext {
	isOpen = $state(false);
	name = $state('');
	count = $state(0);
	createdAt = $state(new SvelteDate());
	selectedIds = $state(new SvelteSet<string>());
	countById = $state(new SvelteMap<string, number>());
	items = $state<string[]>([]);
	url = $state(new SvelteURL('https://example.com'));

	readonly displayName = $derived(this.name.trim() || 'Untitled');
	readonly hasSelection = $derived(this.selectedIds.size > 0);

	constructor(initial?: InitialContextState) {
		this.name = $state(initial?.initialName ?? '');
	}

	open() {
		this.isOpen = true;
	}

	close() {
		this.isOpen = false;
	}

	toggleSelection(id: string) {
		if (this.selectedIds.has(id)) {
			this.selectedIds.delete(id);
			return;
		}

		this.selectedIds.add(id);
	}
}

const FEATURE_CONTEXT_KEY = Symbol('FeatureContext');

// ALWAYS USE SETTERS/GETTERS FOR STATE AND PASS STATE FUNCTIONALLY. NEVER DEFINE IT GLOBALLY!!!!!!!
export function setFeatureContext(initial?: InitialContextState) {
	return setContext(FEATURE_CONTEXT_KEY, new FeatureContext(initial));
}

export function getFeatureContext() {
	return getContext<ReturnType<typeof setFeatureContext>>(FEATURE_CONTEXT_KEY);
}
```

Adapt names to the feature. For example, use `ReportEditorContext`, `setReportEditorContext`, `getReportEditorContext`, and `REPORT_EDITOR_CONTEXT_KEY`.

Rules to preserve:

- Keep mutable shared state in `$state` fields.
- Use `$derived` or `$derived.by` for computed values; getters are not automatically reactive.
- Do not use `$effect` inside context classes for state synchronization.
- Prefer passing source callbacks or deriving from source data instead of copying query data into context state.
- Keep mutation methods explicit and small so child components call named actions instead of rewriting shared logic.
- NEVER DO `export const updates = new UpdateState();`. Instead, implement set/get and pass context around functionaly. NEVER DEFINE THE STATE GLOBALLY!!!!
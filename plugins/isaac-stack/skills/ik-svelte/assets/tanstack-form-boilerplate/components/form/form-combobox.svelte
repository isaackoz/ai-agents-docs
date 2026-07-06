<script lang="ts">
	import CheckIcon from '@lucide/svelte/icons/check';
	import ChevronsUpDownIcon from '@lucide/svelte/icons/chevrons-up-down';
	import SearchIcon from '@lucide/svelte/icons/search';
	import { createVirtualizer } from '@tanstack/svelte-virtual';
	import { tick } from 'svelte';
	import { useFieldContext } from '$lib/forms/form.svelte';
	import { normalizeFieldErrors } from './form-errors';

	export type ComboBoxOption = {
		label: string;
		value: string;
	};

	type Props = {
		labelText?: string;
		descriptionText?: string;
		hideErrors?: boolean;
		options: ComboBoxOption[];
		placeholder?: string;
		searchPlaceholder?: string;
		domId?: string;
		classNames?: {
			root?: string;
			label?: string;
			trigger?: string;
			description?: string;
			errorText?: string;
		};
	};

	const field = useFieldContext<string | string[]>();

	let {
		labelText,
		descriptionText,
		hideErrors = false,
		options,
		placeholder = 'Select an item...',
		searchPlaceholder = 'Search...',
		domId,
		classNames
	}: Props = $props();

	let open = $state(false);
	let search = $state('');
	let triggerRef = $state<HTMLButtonElement>(null!);
	let listRef = $state<HTMLDivElement>(null!);

	const controlId = $derived(domId || field.name);
	const currentValue = $derived(
		Array.isArray(field.state.value) ? (field.state.value[0] ?? '') : (field.state.value ?? '')
	);
	const filteredOptions = $derived(
		search
			? options.filter((option) => option.label.toLowerCase().includes(search.toLowerCase()))
			: options
	);
	const selectedLabel = $derived(options.find((option) => option.value === currentValue)?.label);
	const errorMessages = $derived(normalizeFieldErrors(field.state.meta.errors));

	const virtualizer = $derived.by(() => {
		if (!open || !listRef) return null;
		return createVirtualizer<HTMLDivElement, HTMLDivElement>({
			count: filteredOptions.length,
			getScrollElement: () => listRef,
			estimateSize: () => 40,
			overscan: 5
		});
	});

	function setSelectedValue(value: string) {
		field.setValue((Array.isArray(field.state.value) ? [value] : value) as never);
		open = false;
		search = '';
		tick().then(() => triggerRef?.focus());
	}
</script>

<div class={['relative grid gap-1 text-sm', classNames?.root]}>
	{#if labelText}
		<label class={['font-medium', classNames?.label]} for={controlId}>{labelText}</label>
	{/if}

	<button
		bind:this={triggerRef}
		id={controlId}
		type="button"
		class={[
			'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-left text-sm',
			classNames?.trigger
		]}
		aria-expanded={open}
		aria-haspopup="listbox"
		onclick={() => {
			open = !open;
		}}
		onkeydown={(event) => {
			if (event.key === 'Escape') open = false;
		}}
	>
		<span class={selectedLabel ? 'truncate' : 'truncate text-muted-foreground'}>
			{selectedLabel || placeholder}
		</span>
		<ChevronsUpDownIcon class="ml-2 size-4 shrink-0 opacity-50" />
	</button>

	{#if open}
		<div
			class="absolute top-full z-50 mt-1 w-full rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md"
			role="listbox"
			tabindex="-1"
		>
			<div class="flex items-center border-b border-border px-2">
				<SearchIcon class="mr-2 size-4 shrink-0 opacity-50" />
				<input
					bind:value={search}
					placeholder={searchPlaceholder}
					class="h-10 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
				/>
			</div>

			<div bind:this={listRef} class="max-h-72 overflow-y-auto overflow-x-hidden">
				{#if filteredOptions.length === 0}
					<div class="px-2 py-6 text-center text-sm text-muted-foreground">No items found.</div>
				{:else}
					<div
						style:position="relative"
						style:height="{$virtualizer?.getTotalSize()}px"
						style:width="100%"
					>
						{#each $virtualizer?.getVirtualItems() as row (row.index)}
							{@const option = filteredOptions[row.index]}
							<div
								style="position: absolute; top: 0; left: 0; width: 100%; height: {row.size}px; transform: translateY({row.start}px);"
							>
								<button
									type="button"
									class={[
										'flex h-10 w-full items-center rounded-sm px-2 text-left text-sm hover:bg-accent hover:text-accent-foreground',
										currentValue === option.value && 'bg-accent text-accent-foreground'
									]}
									onclick={() => setSelectedValue(option.value)}
								>
									<CheckIcon
										class={[
											'mr-2 size-4',
											currentValue !== option.value && 'text-transparent'
										]}
									/>
									<span class="truncate">{option.label}</span>
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}

	{#if descriptionText}
		<p class={['text-sm text-muted-foreground', classNames?.description]}>{descriptionText}</p>
	{/if}
	{#if !hideErrors && errorMessages.length > 0}
		<em class={['text-xs text-destructive', classNames?.errorText]}>
			{errorMessages.join(', ')}
		</em>
	{/if}
</div>

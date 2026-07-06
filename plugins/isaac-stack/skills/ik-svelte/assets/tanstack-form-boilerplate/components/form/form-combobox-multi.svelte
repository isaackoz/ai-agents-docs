<script lang="ts">
	import CheckIcon from '@lucide/svelte/icons/check';
	import ChevronsUpDownIcon from '@lucide/svelte/icons/chevrons-up-down';
	import SearchIcon from '@lucide/svelte/icons/search';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import { createVirtualizer } from '@tanstack/svelte-virtual';
	import { useFieldContext } from '$lib/forms/form.svelte';
	import { normalizeFieldErrors } from './form-errors';

	export type ComboBoxMultiOption = {
		label: string;
		value: string;
	};

	type Props = {
		labelText?: string;
		descriptionText?: string;
		hideErrors?: boolean;
		hideSelectedItems?: boolean;
		options: ComboBoxMultiOption[];
		placeholder?: string;
		searchPlaceholder?: string;
		maxItems?: number;
		domId?: string;
		classNames?: {
			root?: string;
			label?: string;
			trigger?: string;
			description?: string;
			errorText?: string;
		};
	};

	const field = useFieldContext<string[]>();

	let {
		labelText,
		descriptionText,
		hideErrors = false,
		hideSelectedItems = false,
		options,
		placeholder = 'Select items...',
		searchPlaceholder = 'Search items...',
		maxItems = Infinity,
		domId,
		classNames
	}: Props = $props();

	let open = $state(false);
	let search = $state('');
	let listRef = $state<HTMLDivElement>(null!);

	const controlId = $derived(domId || field.name);
	const currentValues = $derived(field.state.value ?? []);
	const filteredOptions = $derived(
		search
			? options.filter((option) => option.label.toLowerCase().includes(search.toLowerCase()))
			: options
	);
	const selectedItems = $derived(options.filter((option) => currentValues.includes(option.value)));
	const triggerText = $derived.by(() => {
		if (selectedItems.length === 0) return placeholder;
		const firstLabel = selectedItems[0]?.label ?? '';
		if (selectedItems.length === 1) return firstLabel;
		return `${firstLabel} + ${selectedItems.length - 1} more`;
	});
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

	function toggleValue(value: string) {
		if (currentValues.includes(value)) {
			field.setValue(currentValues.filter((current) => current !== value));
			return;
		}
		if (currentValues.length < maxItems) {
			field.setValue([...currentValues, value]);
		}
	}

	function removeItem(value: string) {
		field.setValue(currentValues.filter((current) => current !== value));
	}
</script>

<div class={['relative grid gap-2 text-sm', classNames?.root]}>
	{#if labelText}
		<label class={['font-medium', classNames?.label]} for={controlId}>{labelText}</label>
	{/if}

	<button
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
		<span class={selectedItems.length > 0 ? 'truncate' : 'truncate text-muted-foreground'}>
			{triggerText}
		</span>
		<ChevronsUpDownIcon class="ml-2 size-4 shrink-0 opacity-50" />
	</button>

	{#if open}
		<div
			class="absolute top-16 z-50 w-full rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md"
			role="listbox"
			tabindex="-1"
			aria-multiselectable="true"
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
							{@const selected = currentValues.includes(option.value)}
							{@const maxed = currentValues.length >= maxItems && !selected}
							<div
								style="position: absolute; top: 0; left: 0; width: 100%; height: {row.size}px; transform: translateY({row.start}px);"
							>
								<button
									type="button"
									disabled={maxed}
									class={[
										'flex h-10 w-full items-center rounded-sm px-2 text-left text-sm hover:bg-accent hover:text-accent-foreground disabled:cursor-not-allowed disabled:opacity-50',
										selected && 'bg-accent text-accent-foreground'
									]}
									onclick={() => toggleValue(option.value)}
								>
									<span
										class={[
											'mr-2 flex size-4 items-center justify-center rounded-sm border border-primary',
											selected ? 'bg-primary text-primary-foreground' : 'opacity-50'
										]}
									>
										{#if selected}
											<CheckIcon class="size-3" />
										{/if}
									</span>
									<span class="truncate">{option.label}</span>
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}

	{#if !hideSelectedItems && selectedItems.length > 0}
		<div class="grid gap-1 rounded-md border border-border p-2">
			{#each selectedItems as item (item.value)}
				<div class="flex items-center justify-between gap-2 rounded-md bg-muted px-2 py-1 text-sm">
					<span class="truncate">{item.label}</span>
					<button
						type="button"
						class="rounded p-1 text-destructive hover:bg-destructive/10"
						aria-label="Remove {item.label}"
						onclick={() => removeItem(item.value)}
					>
						<Trash2Icon class="size-3" />
					</button>
				</div>
			{/each}
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

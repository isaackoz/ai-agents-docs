<script lang="ts">
	import { useFieldContext } from '$lib/forms/form.svelte';
	import type { HTMLSelectAttributes } from 'svelte/elements';
	import { normalizeFieldErrors } from './form-errors';

	export type SelectOption = {
		label: string;
		value: string;
	};

	type Props = {
		labelText?: string;
		descriptionText?: string;
		hideErrors?: boolean;
		options: SelectOption[];
		placeholder?: string;
		selectProps?: HTMLSelectAttributes;
		class?: string;
	};

	const field = useFieldContext<string>();

	let {
		labelText,
		descriptionText,
		hideErrors = false,
		options,
		placeholder = 'Select a value',
		selectProps = {},
		class: className = ''
	}: Props = $props();

	const controlId = $derived(selectProps.id ?? field.name);
	const errorMessages = $derived(normalizeFieldErrors(field.state.meta.errors));
</script>

<label class={className ? `grid gap-1 text-sm ${className}` : 'grid gap-1 text-sm'} for={controlId}>
	{#if labelText}
		<span class="font-medium">{labelText}</span>
	{/if}
	<select
		{...selectProps}
		id={controlId}
		name={field.name}
		value={field.state.value ?? ''}
		onchange={(event) => field.handleChange(event.currentTarget.value)}
		onblur={field.handleBlur}
		class={selectProps.class ??
			'h-10 rounded-md border border-input bg-background px-3 py-2 text-sm'}
	>
		<option value="">{placeholder}</option>
		{#each options as option (option.value)}
			<option value={option.value}>{option.label}</option>
		{/each}
	</select>
	{#if descriptionText}
		<p class="text-sm text-muted-foreground">{descriptionText}</p>
	{/if}
	{#if !hideErrors && errorMessages.length > 0}
		<em class="text-xs text-destructive">{errorMessages.join(', ')}</em>
	{/if}
</label>

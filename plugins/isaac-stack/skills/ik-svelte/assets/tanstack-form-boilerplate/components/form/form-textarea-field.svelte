<script lang="ts">
	import { useFieldContext } from '$lib/forms/form.svelte';
	import type { HTMLTextareaAttributes } from 'svelte/elements';
	import { normalizeFieldErrors } from './form-errors';

	type Props = {
		labelText?: string;
		descriptionText?: string;
		hideErrors?: boolean;
		textareaProps?: HTMLTextareaAttributes;
		class?: string;
	};

	const field = useFieldContext<string>();

	let {
		labelText,
		descriptionText,
		hideErrors = false,
		textareaProps = {},
		class: className = ''
	}: Props = $props();

	const controlId = $derived(textareaProps.id ?? field.name);
	const errorMessages = $derived(normalizeFieldErrors(field.state.meta.errors));
</script>

<label class={className ? `grid gap-1 text-sm ${className}` : 'grid gap-1 text-sm'} for={controlId}>
	{#if labelText}
		<span class="font-medium">{labelText}</span>
	{/if}
	<textarea
		{...textareaProps}
		id={controlId}
		name={field.name}
		value={field.state.value ?? ''}
		oninput={(event) => field.handleChange(event.currentTarget.value)}
		onblur={field.handleBlur}
		class={textareaProps.class ??
			'min-h-24 rounded-md border border-input bg-background px-3 py-2 text-sm'}
	></textarea>
	{#if descriptionText}
		<p class="text-sm text-muted-foreground">{descriptionText}</p>
	{/if}
	{#if !hideErrors && errorMessages.length > 0}
		<em class="text-xs text-destructive">{errorMessages.join(', ')}</em>
	{/if}
</label>

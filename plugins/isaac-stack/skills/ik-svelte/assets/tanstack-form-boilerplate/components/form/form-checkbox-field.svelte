<script lang="ts">
	import { useFieldContext } from '$lib/forms/form.svelte';
	import type { HTMLInputAttributes } from 'svelte/elements';
	import { normalizeFieldErrors } from './form-errors';

	type Props = {
		labelText?: string;
		descriptionText?: string;
		hideErrors?: boolean;
		inputProps?: HTMLInputAttributes;
		class?: string;
	};

	const field = useFieldContext<boolean>();

	let {
		labelText,
		descriptionText,
		hideErrors = false,
		inputProps = {},
		class: className = ''
	}: Props = $props();

	const controlId = $derived(inputProps.id ?? field.name);
	const errorMessages = $derived(normalizeFieldErrors(field.state.meta.errors));
</script>

<div class={className ? `grid gap-1 text-sm ${className}` : 'grid gap-1 text-sm'}>
	<label class="flex items-start gap-3" for={controlId}>
		<input
			{...inputProps}
			id={controlId}
			name={field.name}
			type="checkbox"
			checked={Boolean(field.state.value)}
			onchange={(event) => field.handleChange(event.currentTarget.checked)}
			onblur={field.handleBlur}
			class={inputProps.class ?? 'mt-1 size-4 rounded border-input'}
		/>
		<span class="grid gap-1">
			{#if labelText}
				<span class="font-medium">{labelText}</span>
			{/if}
			{#if descriptionText}
				<span class="text-sm text-muted-foreground">{descriptionText}</span>
			{/if}
		</span>
	</label>
	{#if !hideErrors && errorMessages.length > 0}
		<em class="text-xs text-destructive">{errorMessages.join(', ')}</em>
	{/if}
</div>

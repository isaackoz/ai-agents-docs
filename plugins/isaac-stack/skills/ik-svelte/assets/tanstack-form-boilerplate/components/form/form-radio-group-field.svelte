<script lang="ts">
	import { useFieldContext } from '$lib/forms/form.svelte';
	import { normalizeFieldErrors } from './form-errors';

	export type RadioOption = {
		label: string;
		value: string;
	};

	type Props = {
		labelText?: string;
		descriptionText?: string;
		hideErrors?: boolean;
		disabled?: boolean;
		options: RadioOption[];
		classNames?: {
			root?: string;
			label?: string;
			option?: string;
			description?: string;
			errorText?: string;
		};
	};

	const field = useFieldContext<string>();

	let {
		labelText,
		descriptionText,
		hideErrors = false,
		disabled = false,
		options,
		classNames
	}: Props = $props();

	const errorMessages = $derived(normalizeFieldErrors(field.state.meta.errors));
</script>

<fieldset class={['grid gap-2 text-sm', classNames?.root]} {disabled}>
	{#if labelText}
		<legend class={['font-medium', classNames?.label]}>{labelText}</legend>
	{/if}
	<div class="grid gap-2">
		{#each options as option (option.value)}
			<label
				class={[
					'flex items-center gap-3 rounded-md border border-input px-3 py-2',
					classNames?.option
				]}
			>
				<input
					type="radio"
					name={field.name}
					value={option.value}
					checked={field.state.value === option.value}
					onchange={() => field.handleChange(option.value)}
					onblur={field.handleBlur}
				/>
				<span>{option.label}</span>
			</label>
		{/each}
	</div>
	{#if descriptionText}
		<p class={['text-sm text-muted-foreground', classNames?.description]}>{descriptionText}</p>
	{/if}
	{#if !hideErrors && errorMessages.length > 0}
		<em class={['text-xs text-destructive', classNames?.errorText]}>
			{errorMessages.join(', ')}
		</em>
	{/if}
</fieldset>

<script lang="ts">
	import { useFormContext } from '$lib/forms/form.svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';

	type Props = {
		label?: string;
		submittingLabel?: string;
		disabled?: boolean;
		buttonProps?: HTMLButtonAttributes;
	};

	const form = useFormContext();

	let {
		label = 'Submit',
		submittingLabel = 'Submitting...',
		disabled = false,
		buttonProps = {}
	}: Props = $props();
</script>

<form.Subscribe selector={(state) => state.isSubmitting}>
	{#snippet children(isSubmitting)}
		<button
			{...buttonProps}
			type="submit"
			disabled={isSubmitting || disabled || Boolean(buttonProps.disabled)}
			class={buttonProps.class ??
				'h-10 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50'}
		>
			{isSubmitting ? submittingLabel : label}
		</button>
	{/snippet}
</form.Subscribe>

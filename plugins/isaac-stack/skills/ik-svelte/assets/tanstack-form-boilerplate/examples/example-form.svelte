<script lang="ts">
	import { createAppForm } from '$lib/forms/form.svelte';

	type ContactFormValues = {
		name: string;
		email: string;
		role: string;
		department: string;
		skills: string[];
		startDate: string;
		contactMethod: string;
		notes: string;
		subscribed: boolean;
	};

	let {
		onSave = async () => {}
	}: {
		onSave?: (value: ContactFormValues) => void | Promise<void>;
	} = $props();

	const departmentOptions = [
		{ label: 'Operations', value: 'operations' },
		{ label: 'Finance', value: 'finance' },
		{ label: 'Sales', value: 'sales' },
		{ label: 'Support', value: 'support' }
	];
	const skillOptions = Array.from({ length: 250 }, (_, index) => ({
		label: `Skill ${index + 1}`,
		value: `skill-${index + 1}`
	}));
	const contactMethodOptions = [
		{ label: 'Email', value: 'email' },
		{ label: 'Phone', value: 'phone' }
	];

	const form = createAppForm(() => ({
		defaultValues: {
			name: '',
			email: '',
			role: '',
			department: '',
			skills: [],
			startDate: '',
			contactMethod: 'email',
			notes: '',
			subscribed: false
		} satisfies ContactFormValues,
		validators: {
			onSubmit({ value }) {
				const fields: Partial<Record<keyof ContactFormValues, string>> = {};
				if (!value.name.trim()) fields.name = 'Enter a name.';
				if (!value.email.includes('@')) fields.email = 'Enter a valid email.';
				if (!value.role) fields.role = 'Choose a role.';
				if (!value.department) fields.department = 'Choose a department.';
				if (value.skills.length === 0) fields.skills = 'Choose at least one skill.';
				return Object.keys(fields).length === 0 ? undefined : { fields };
			}
		},
		async onSubmit({ value }) {
			await onSave(value);
		}
	}));
</script>

<form
	class="grid gap-4"
	onsubmit={(event) => {
		event.preventDefault();
		form.handleSubmit();
	}}
>
	<form.AppField name="name">
		{#snippet children(field)}
			<field.InputField labelText="Name" inputProps={{ autocomplete: 'name' }} />
		{/snippet}
	</form.AppField>

	<form.AppField name="email">
		{#snippet children(field)}
			<field.InputField labelText="Email" inputProps={{ type: 'email', autocomplete: 'email' }} />
		{/snippet}
	</form.AppField>

	<form.AppField name="role">
		{#snippet children(field)}
			<field.SelectField
				labelText="Role"
				options={[
					{ label: 'Admin', value: 'admin' },
					{ label: 'Member', value: 'member' }
				]}
			/>
		{/snippet}
	</form.AppField>

	<form.AppField name="department">
		{#snippet children(field)}
			<field.ComboBox labelText="Department" options={departmentOptions} />
		{/snippet}
	</form.AppField>

	<form.AppField name="skills">
		{#snippet children(field)}
			<field.ComboBoxMulti
				labelText="Skills"
				descriptionText="This starter uses TanStack Virtual for long option lists."
				options={skillOptions}
				maxItems={5}
			/>
		{/snippet}
	</form.AppField>

	<form.AppField name="startDate">
		{#snippet children(field)}
			<field.DatePicker labelText="Start date" />
		{/snippet}
	</form.AppField>

	<form.AppField name="contactMethod">
		{#snippet children(field)}
			<field.RadioGroupField labelText="Preferred contact" options={contactMethodOptions} />
		{/snippet}
	</form.AppField>

	<form.AppField name="notes">
		{#snippet children(field)}
			<field.TextareaField labelText="Notes" />
		{/snippet}
	</form.AppField>

	<form.AppField name="subscribed">
		{#snippet children(field)}
			<field.CheckboxField labelText="Send updates" />
		{/snippet}
	</form.AppField>

	<form.AppForm>
		<form.SubmitButton label="Save" />
	</form.AppForm>
</form>

import FormComboboxMulti from '$lib/components/form/form-combobox-multi.svelte';
import FormCombobox from '$lib/components/form/form-combobox.svelte';
import FormCheckboxField from '$lib/components/form/form-checkbox-field.svelte';
import FormDateField from '$lib/components/form/form-date-field.svelte';
import FormInputField from '$lib/components/form/form-input-field.svelte';
import FormRadioGroupField from '$lib/components/form/form-radio-group-field.svelte';
import FormSelectField from '$lib/components/form/form-select-field.svelte';
import FormSubmitButton from '$lib/components/form/form-submit-button.svelte';
import FormTextareaField from '$lib/components/form/form-textarea-field.svelte';
import { createFormCreator, createFormCreatorContexts } from '@tanstack/svelte-form';

export const { createAppForm } = createFormCreator({
	fieldComponents: {
		InputField: FormInputField,
		TextareaField: FormTextareaField,
		SelectField: FormSelectField,
		NativeSelect: FormSelectField,
		ComboBox: FormCombobox,
		ComboBoxMulti: FormComboboxMulti,
		DatePicker: FormDateField,
		CheckboxField: FormCheckboxField,
		RadioGroupField: FormRadioGroupField
	},
	formComponents: {
		SubmitButton: FormSubmitButton
	}
});

export const { useFieldContext, useFormContext } = createFormCreatorContexts();

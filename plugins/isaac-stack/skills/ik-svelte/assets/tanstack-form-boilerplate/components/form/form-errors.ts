// normalizeFieldErrors keeps field components compatible with string, Error-like, and nested validators.
export function normalizeFieldErrors(errors: unknown[]): string[] {
	const messages: string[] = [];

	function pushMessage(value: unknown) {
		if (Array.isArray(value)) {
			value.forEach(pushMessage);
			return;
		}
		if (typeof value === 'string' && value.trim() !== '') {
			const message = value.trim();
			if (!messages.includes(message)) messages.push(message);
			return;
		}
		if (
			value &&
			typeof value === 'object' &&
			'message' in value &&
			typeof value.message === 'string'
		) {
			pushMessage(value.message);
		}
	}

	errors.forEach(pushMessage);
	return messages;
}

import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const sessionId = event.cookies.get('sessionId');

	if (sessionId) {
		throw redirect(301, '/');
	}
};

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const email = formData.get('email');
		const password = formData.get('password');
		const confirmPassword = formData.get('confirmPassword');

		console.log('Passwords do not match');
		if (password !== confirmPassword) {
			return { status: 400, body: JSON.stringify({ error: 'Passwords do not match' }) };
		}
		const body = JSON.stringify({ email, password });

		console.log(body);

		throw redirect(301, '/');
	}
} satisfies Actions;

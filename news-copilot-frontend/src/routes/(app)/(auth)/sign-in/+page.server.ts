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
		const remember = formData.get('remember');
		const body = JSON.stringify({ email, password });

		if (remember) console.log('Remember me checked');

		console.log(body);

		throw redirect(301, '/');
	}
} satisfies Actions;

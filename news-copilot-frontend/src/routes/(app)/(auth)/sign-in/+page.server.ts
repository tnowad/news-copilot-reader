import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import authService from '$lib/services/auth.service';

export const load: PageServerLoad = async (event) => {
	const sessionId = event.cookies.get('sessionId');

	if (sessionId) {
		throw redirect(301, '/');
	}
};

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const email = formData.get('email') as string;
		const password = formData.get('password') as string;
		const remember = formData.get('remember');

		if (remember) console.log('Remember me checked');

		const response = await authService.signIn({ email, password });

		console.log(response);

		throw redirect(301, '/');
	}
} satisfies Actions;

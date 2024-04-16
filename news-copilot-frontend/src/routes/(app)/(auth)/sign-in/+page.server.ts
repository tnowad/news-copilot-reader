import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import authService from '$lib/services/auth.service';
import { StatusCodes } from 'http-status-codes';

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const email = formData.get('email') as string;
		const password = formData.get('password') as string;
		const remember = (formData.get('remember') as null | 'on') === 'on';

		if (remember) {
			console.log(remember);
		}

		const response = await authService.signIn({ email, password });

		switch (response.statusCode) {
			case StatusCodes.OK:
				event.cookies.set('refreshToken', response.data.token.refreshToken, { path: '/' });
				event.cookies.set('accessToken', response.data.token.accessToken, { path: '/' });
				return { ...response, redirectTo: '/' };
				break;
		}

		return response;
	}
} satisfies Actions;

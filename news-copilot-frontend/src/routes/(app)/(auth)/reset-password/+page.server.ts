import authService from '$lib/services/auth.service';
import { StatusCodes } from 'http-status-codes';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const email = event.url.searchParams.get('email') as string;
	return {
		email
	};
};

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const email = formData.get('email') as string;
		const code = formData.get('code') as string;
		const password = formData.get('password') as string;
		const confirmPassword = formData.get('confirmPassword') as string;

		const response = await authService.resetPassword({ code, email, password, confirmPassword });

		switch (response.statusCode) {
			case StatusCodes.OK:
				return {
					...response,
					redirectTo: '/sign-in'
				};
		}

		return response;
	}
} satisfies Actions;

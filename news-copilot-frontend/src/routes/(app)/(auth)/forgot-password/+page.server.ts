import { type Actions } from '@sveltejs/kit';
import authService from '$lib/services/auth.service';
import { StatusCodes } from 'http-status-codes';

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const email = formData.get('email') as string;

		const response = await authService.forgotPassword({ email });

		switch (response.statusCode) {
			case StatusCodes.OK:
				return { ...response, redirectTo: '/reset-password' + '?email=' + email };
		}

		return response;
	}
} satisfies Actions;

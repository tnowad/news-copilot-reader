import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import authService from '$lib/services/auth.service';
import { StatusCodes } from 'http-status-codes';

export const load: PageServerLoad = async (event) => {
	const accessToken = event.cookies.get('accessToken');

	if (accessToken) {
		return redirect(StatusCodes.MOVED_TEMPORARILY, '/');
	}
};

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const email = formData.get('email') as string;
		const password = formData.get('password') as string;
		const confirmPassword = formData.get('confirmPassword') as string;
		const displayName = formData.get('displayName') as string;
		const acceptTerms = (formData.get('acceptTerms') as null | 'on') === 'on';

		const response = await authService.signUp({
			email,
			displayName,
			password,
			confirmPassword,
			acceptTerms
		});

		switch (response.statusCode) {
			case StatusCodes.CREATED:
				console.log('Sign up successful');
				event.cookies.set('refreshToken', response.data.token.refreshToken, { path: '/' });
				event.cookies.set('accessToken', response.data.token.accessToken, { path: '/' });
				break;
			case StatusCodes.CONFLICT:
			case StatusCodes.BAD_REQUEST:
				console.log('Sign in failed');
				break;
			case StatusCodes.UNPROCESSABLE_ENTITY:
				console.log('Sign in validation failed');
				break;
			default:
				console.log('Unknown status code');
		}

		return response;
	}
} satisfies Actions;

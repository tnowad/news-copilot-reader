import userService from '$lib/services/user.service';
import { StatusCodes } from 'http-status-codes';
import type { Actions, PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
	const accessToken = event.cookies.get('accessToken');
	const id = +event.params.id;

	if (!accessToken) {
		redirect(StatusCodes.TEMPORARY_REDIRECT, '/sign-in');
	}

	const userResponse = await userService.getUser(
		{ include: ['roles'], style: 'full', id },
		{ Authorization: `Bearer ${accessToken}` }
	);

	const user = userResponse.statusCode === StatusCodes.OK ? userResponse.data.user : null;

	return { user: user };
};

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const email = formData.get('email') as string;
		const birthDate = formData.get('birthDate') as string;
		const phoneNumber = formData.get('phoneNumber') as string;
		const password = formData.get('password') as string;
		const newPassword = formData.get('newPassword') as string;
		const displayName = formData.get('displayName') as string;
		const avatarImage = formData.get('avatarImage') as string;
		const bio = formData.get('bio') as string;

		// Change to update user id
		const response = await userService.updateCurrentUser(
			{
				email,
				avatarImage,
				displayName,
				bio,
				phoneNumber,
				birthDate,
				newPassword,
				password
			},
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);

		switch (response.statusCode) {
			case StatusCodes.OK:
				break;
			case StatusCodes.NOT_FOUND:
			case StatusCodes.FORBIDDEN:
				break;
			case StatusCodes.UNPROCESSABLE_ENTITY:
				break;
			default:
		}

		return response;
	}
} satisfies Actions;

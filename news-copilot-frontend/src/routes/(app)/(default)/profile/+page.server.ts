import { StatusCodes } from 'http-status-codes';
import type { Actions, PageServerLoad } from './$types';
import userService from '$lib/services/user.service';
import uploadService from '$lib/services/upload.service';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
	const accessToken = event.cookies.get('accessToken');

	if (!accessToken) {
		redirect(StatusCodes.TEMPORARY_REDIRECT, '/sign-in');
	}

	const currentUserProfileResponse = await userService.getCurrentUserProfile(
		{ include: ['roles'], style: 'full' },
		{ Authorization: `Bearer ${accessToken}` }
	);

	const user =
		currentUserProfileResponse.statusCode === StatusCodes.OK
			? currentUserProfileResponse.data.user
			: null;

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
		let avatarURL;

		const body = {
			email,
			displayName,
			bio,
			phoneNumber,
			birthDate,
			newPassword,
			password
		};
		if (avatarImage) {
			avatarURL = await uploadService.uploadFile(avatarImage);
			body['avatarImage'] = avatarURL;
		}
		const response = await userService.updateCurrentUser(body, {
			Authorization: `Bearer ${event.cookies.get('accessToken')}`
		});

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

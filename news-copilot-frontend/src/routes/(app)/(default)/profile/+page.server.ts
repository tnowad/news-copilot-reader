import userService from '$lib/services/user.service';
import { StatusCodes } from 'http-status-codes';
import type { Actions, PageServerLoad } from './$types';
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

		console.log(email, birthDate, password, newPassword, displayName, bio, phoneNumber)
		const response = await userService.updateCurrentUser({ email, avatarImage, displayName, bio, phoneNumber, birthDate });


		switch (response.statusCode) {
			case StatusCodes.OK:
				console.log('Profile update successful');
				break;
			case StatusCodes.NOT_FOUND:
			case StatusCodes.FORBIDDEN:
				console.log('Profile update failed');
				break;
			case StatusCodes.UNPROCESSABLE_ENTITY:
				console.log('Profile update validation failed');
				break;
			default:
				console.log('Unknown status code');
		}

		return response;
	}
} satisfies Actions;	

import userService from '$lib/services/user.service';
import { StatusCodes } from 'http-status-codes';
import type { PageServerLoad } from './$types';
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

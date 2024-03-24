import userService from '$lib/services/user.service';
import { StatusCodes } from 'http-status-codes';
import type { PageServerLoad } from './$types';
// Todo load current user
export const load: PageServerLoad = async (event) => {
	const accessToken = event.cookies.get('accessToken');

	const currentUserProfileResponse = await userService.getCurrentUserProfile(
		{ include: ['roles', 'avatarImage'] },
		{ Authorization: `Bearer ${accessToken}` }
	);

	switch (currentUserProfileResponse.statusCode) {
		case StatusCodes.OK:
			event.locals.user = currentUserProfileResponse.data.user;
			break;
		case StatusCodes.UNAUTHORIZED | StatusCodes.FORBIDDEN:
			console.error('Failed to get current user:', currentUserProfileResponse.message);
			break;
		default:
			break;
	}

	return { user: event.locals.user };
};

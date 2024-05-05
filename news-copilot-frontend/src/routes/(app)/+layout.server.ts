import userService from '$lib/services/user.service';
import { StatusCodes } from 'http-status-codes';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async (event) => {
	const accessToken = event.cookies.get('accessToken');

	const currentUserProfileResponse = await userService.getCurrentUserProfile(
		{
			include: ['roles']
		},
		{
			Authorization: `Bearer ${accessToken}`
		}
	);

	let user = null;

	switch (currentUserProfileResponse.statusCode) {
		case StatusCodes.OK:
			user = currentUserProfileResponse.data.user;
			break;
		case StatusCodes.UNAUTHORIZED:
			user = null;
			break;
		default:
			break;
	}

	return {
		user
	};
};

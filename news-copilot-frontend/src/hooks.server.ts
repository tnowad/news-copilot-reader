import authService from '$lib/services/auth.service';
import userService from '$lib/services/user.service';
import type { Handle, RequestEvent } from '@sveltejs/kit';
import { StatusCodes } from 'http-status-codes';
import jwt, { type JwtPayload } from 'jsonwebtoken';

export const handle: Handle = async ({ event, resolve }) => {
	await processTokens(event);
	await getCurrentUser(event);

	return await resolve(event);
};

const processTokens = async (event: RequestEvent) => {
	const accessToken = event.cookies.get('accessToken');
	const refreshToken = event.cookies.get('refreshToken');
	if (accessToken) {
		try {
			const decoded = jwt.decode(accessToken) as JwtPayload;
			if (!decoded) {
				throw new Error('Invalid token');
			}

			const currentTime = Math.floor(Date.now() / 1000);

			if (decoded?.exp && decoded.exp < currentTime) {
				throw new Error('Token expired');
			}
		} catch (error) {
			event.cookies.delete('accessToken', { path: '/' });
			await tryRefreshToken(event);
		}
	} else if (refreshToken) {
		await tryRefreshToken(event);
	}
};

const tryRefreshToken = async (event: RequestEvent) => {
	const refreshToken = event.cookies.get('refreshToken');
	if (refreshToken) {
		try {
			await refreshAccessToken(event);
		} catch (error) {
			event.cookies.delete('refreshToken', { path: '/' });
		}
	}
};

const refreshAccessToken = async (event: RequestEvent) => {
	const refreshToken = event.cookies.get('refreshToken');
	if (!refreshToken) {
		return;
	}

	const response = await authService.refreshToken(
		{ refreshToken },
		{ Authorization: `Bearer ${refreshToken}` }
	);

	switch (response.statusCode) {
		case StatusCodes.OK:
			event.cookies.set('accessToken', response.data.token.accessToken, { path: '/' });
			break;
		case StatusCodes.UNAUTHORIZED:
			console.error('Failed to refresh token:', response.message);
			event.cookies.delete('accessToken', { path: '/' });
			event.cookies.delete('refreshToken', { path: '/' });
			break;
		default:
			console.error('Unexpected status code');
			break;
	}
};

const getCurrentUser = async (event: RequestEvent) => {
	const accessToken = event.cookies.get('accessToken');

	const currentUserProfileResponse = await userService.getCurrentUserProfile(
		{
			include: ['roles', 'avatarImage']
		},
		{
			Authorization: `Bearer ${accessToken}`
		}
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
};

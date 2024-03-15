import authService from '$lib/services/auth.service';
import type { Handle, RequestEvent } from '@sveltejs/kit';
import { StatusCodes } from 'http-status-codes';
import jwt, { type JwtPayload } from 'jsonwebtoken';

export const handle: Handle = async ({ event, resolve }) => {
	const accessToken = event.cookies.get('accessToken');
	const refreshToken = event.cookies.get('refreshToken');

	if (accessToken && accessToken !== 'null') {
		try {
			const decoded = jwt.decode(accessToken) as JwtPayload;
			const currentTime = Math.floor(Date.now() / 1000);

			if (decoded.exp && decoded.exp < currentTime && refreshToken) {
				await refreshAccessToken(event, refreshToken);
			}
		} catch (error) {
			console.error('Error decoding accessToken:', error);
		}
	} else if (refreshToken) {
		await refreshAccessToken(event, refreshToken);
	}

	console.log(event);

	return await resolve(event);
};

async function refreshAccessToken(event: RequestEvent, refreshToken: string) {
	const response = await authService.refreshToken({ refreshToken });

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
}

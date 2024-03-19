import { StatusCodes } from 'http-status-codes';
import type { Actions } from './$types';
import { redirect } from '@sveltejs/kit';

export const actions: Actions = {
	default: async (event) => {
		event.cookies.delete('accessToken', { path: '/' });
		event.cookies.delete('refreshToken', { path: '/' });

		redirect(StatusCodes.MOVED_TEMPORARILY, '/');
	}
};

import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { StatusCodes } from 'http-status-codes';

export const load: LayoutServerLoad = async (event) => {
	if (!event.locals.user?.roles?.some((role) => role === 'ADMIN' || role === 'WRITER')) {
		redirect(StatusCodes.TEMPORARY_REDIRECT, '/');
	}
	return {
		user: event.locals.user
	};
};

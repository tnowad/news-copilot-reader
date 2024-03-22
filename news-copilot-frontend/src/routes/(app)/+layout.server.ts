import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async (event) => {
	console.log('layout server load', event.locals.user);
	return { user: event.locals.user };
};

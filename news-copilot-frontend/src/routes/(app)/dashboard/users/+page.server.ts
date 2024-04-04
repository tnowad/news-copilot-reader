import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { StatusCodes } from 'http-status-codes';
import userService from '$lib/services/user.service';

export const load: PageServerLoad = async (event) => {
	const page = parseInt(event.url.searchParams.get('page') ?? '1');
	const limit = parseInt(event.url.searchParams.get('limit') ?? '10');
	const search = event.url.searchParams.get('search') ?? '';

	// const usersResponse = await userService.getAllUsers({
	// 	includes: ['roles'],
	// 	page: page,
	// 	limit: limit,
	// 	search: search
	// });

	return {
		// users: usresResponse.statusCode === StatusCodes.OK ? usersResponse.data.users : [],
		// metadata: usresResponse.statusCode === StatusCodes.OK ? usersResponse.data.metadata : null
	};
};

import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { StatusCodes } from 'http-status-codes';
import userService from '$lib/services/user.service';

export const load: PageServerLoad = async (event) => {
	const id = parseInt(event.url.searchParams.get('id') ?? '1');
	const limit = parseInt(event.url.searchParams.get('limit') ?? '10');
	const search = event.url.searchParams.get('search') ?? '';

	const accessToken = event.cookies.get('accessToken');
	const usersResponse = await userService.getAllUsers(
		{
			includes: ['roles'],
			id: id,
			limit: limit,
			search: search
		},
		{
			Authorization: `Bearer ${accessToken}`
		}
	);
	console.log(usersResponse);

	return {
		users: usersResponse.statusCode === StatusCodes.OK ? usersResponse.data.users : []
		// metadata: usersResponse.statusCode === StatusCodes.OK ? usersResponse.data.metadata : null
	};
};

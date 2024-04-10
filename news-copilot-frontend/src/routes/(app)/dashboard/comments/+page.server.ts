import articleService from '$lib/services/article.service';
import commentServerices from '$lib/services/comment.service';
import { redirect } from '@sveltejs/kit';
import { StatusCodes } from 'http-status-codes';

export const load = async (event) => {

	if (!event.locals.user.roles?.some(role => role == 'ADMIN')) {
		redirect(StatusCodes.TEMPORARY_REDIRECT, '/');

	}

	const page = parseInt(event.url.searchParams.get('page') ?? 1);
	const limit = parseInt(event.url.searchParams.get('limit') ?? 10);
	const search = event.url.searchParams.get('search') ?? '';

	const commentsResponse = await commentServerices.getAllComments({
		includes: ['author', 'article'],
		page: page,
		limit: limit,
		search: search
	});
	console.log(commentsResponse.data.comments);

	return {
		comments: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.comments : [],
		metadata: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.metadata : null
	};
};

import commentServerices from '$lib/services/comment.service';
import { redirect } from '@sveltejs/kit';
import { StatusCodes } from 'http-status-codes';
import type { Actions } from './$types';

export const load = async (event) => {
	if (!event.locals.user.roles?.some((role) => role == 'ADMIN')) {
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
	//console.log(commentsResponse.data.comments);

	return {
		comments: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.comments : [],
		metadata: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.metadata : null
	};
};
export const actions = {
	getAllComment: async (event) => {
		const formData = await event.request.formData();
		if (!event.locals.user) {
			return;
		}
		const sortOrder = formData.get('sortOrder') as string;
		const sortBy = formData.get('sortBy') as string;
		console.log(sortOrder);

		const commentsResponse = await commentServerices.getAllComments({
			sortOrder: sortOrder === 'asc' || sortOrder === 'desc' ? sortOrder : undefined,
			sortBy:
				sortBy === 'article' || sortBy === 'user' || sortBy === 'createdAt' ? sortBy : undefined
		});
		console.log(commentsResponse.data.comments);
		return {
			comments: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.comments : []
		};
	},
	deleteComment: async (event) => {
		const formData = await event.request.formData();
		const commentId = formData.get('commentId') as unknown as number;
		const deleteCommentResponse = await commentServerices.deleteComment(
			{
				id: commentId
			},
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);
		return deleteCommentResponse;
	}
} satisfies Actions;

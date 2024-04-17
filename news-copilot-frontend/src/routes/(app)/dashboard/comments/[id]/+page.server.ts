import commentServerices from '$lib/services/comment.service';
import { StatusCodes } from 'http-status-codes';
import type { Actions } from '../$types';
export const load = async (event: any) => {
	const page = parseInt(event.url.searchParams.get('page') ?? 1);
	const limit = parseInt(event.url.searchParams.get('limit') ?? 10);
	const search = event.url.searchParams.get('search') ?? '';
	const commentsResponse = await commentServerices.getAllComments({
		includes: ['author'],
		page: page,
		limit: limit
	});
	return {
		comments: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.comments : [],
		metadata: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.metadata : null
	};
};
export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		if (!event.locals.user) {
			return;
		}
		const id = event.params.id as unknown as number;
		const content = formData.get('description') as string;
		const authorId = event.locals.user.id as number;

		const commentsResponse = await commentServerices.updateComment({ id: id, content: content, authorId: authorId }, { Authorization: `Bearer ${event.cookies.get('accessToken')}` });

		console.log(commentsResponse.data.comments);
	}
} satisfies Actions;


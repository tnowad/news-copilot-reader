import commentServerices from '$lib/services/comment.service';
import { StatusCodes } from 'http-status-codes';
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

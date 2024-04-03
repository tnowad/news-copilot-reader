import type { PageServerLoad } from './$types';
import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import commentsService from '$lib/services/comment.service';

export const load: PageServerLoad = async ({ params }) => {
	const id = parseInt(params.id);

	const articlesResponse = await articleService.getArticleById({
		id: id,
		includes: ['author', 'categories', 'comments'],
		style: 'full'
	});

	// const commentsResponse = await commentsService.getAllComments({
	//   articleId: id,
	//   include: ['author']
	// })

	return {
		article: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.article : null
		// comments: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.comments : [],
		// commentsMetadata: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.metadata : null
	};
};

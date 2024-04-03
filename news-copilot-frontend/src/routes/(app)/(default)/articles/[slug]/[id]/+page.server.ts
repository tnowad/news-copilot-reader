import type { Actions, PageServerLoad } from './$types';
import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import commentsService from '$lib/services/comment.service';
import authService from '$lib/services/auth.service';
export const load: PageServerLoad = async ({ params }) => {
	const id = parseInt(params.id);

	const articlesResponse = await articleService.getArticleById({
		id: id,
		includes: ['author', 'categories', 'comments'],
		style: 'full'
	});

	const commentsResponse = await commentsService.getAllComments({
		articleId: id,
		includes: ['author'],
		limit: 1000
	})
	const article = articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.article : null;
	const comments = commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.comments : [];
	return {
		article,
		comments
		// commentsMetadata: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.metadata : null
	};
};
export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		if (!event.locals.user) {
			return
		}
		const content = formData.get('content') as string;
		const articleId = parseInt(event.params.id) as number;
		const authorId = event.locals.user.id
		console.log(content);
		console.log(articleId);
		console.log(authorId);
		
		const commentsResponse = await commentsService.createComment(
			{ content: content, authorId: authorId, articleId: articleId },
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		)
		
		console.log(commentsResponse)

	}





} satisfies Actions
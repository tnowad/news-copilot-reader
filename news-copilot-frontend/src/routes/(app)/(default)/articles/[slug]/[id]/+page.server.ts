import type { Actions, PageServerLoad } from './$types';
import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import commentsService from '$lib/services/comment.service';
import viewService from '$lib/services/view.service';
import bookmarksService from '$lib/services/bookmark.service';
export const load: PageServerLoad = async ({ params, locals }) => {
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
	});

	const recommendArticlesResponse = await articleService.getRecommendArticles({
		userId: locals.user?.id,
		articleId: id,
		limit: 12,
		includes: ['author', 'categories']
	});

	const article =
		articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.article : null;
	const comments =
		commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.comments : [];
	return {
		article,
		comments,
		recommendArticles:
			recommendArticlesResponse.statusCode === StatusCodes.OK
				? recommendArticlesResponse.data.articles
				: []
		// commentsMetadata: commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.metadata : null
	};
};
export const actions = {
	createComment: async (event) => {
		const formData = await event.request.formData();
		if (!event.locals.user) {
			return;
		}
		const content = formData.get('content') as string;
		const articleId = parseInt(event.params.id) as number;
		const authorId = event.locals.user.id;

		const commentsResponse = await commentsService.createComment(
			{ content: content, authorId: authorId, articleId: articleId },
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);

		console.log(commentsResponse);
	},
	markViewed: async (event) => {
		const articleId = parseInt(event.params.id);
		await viewService.markArticleViewed(
			{ articleId: articleId },
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);
	},
	bookmarkArticle: async (event) => {
		try {
			const articleId = parseInt(event.params.id);

			// Call the bookmarks service to bookmark the article
			const bookmarkResponse = await bookmarksService.createBookmark(
				{ article_id: articleId }, // Ensure the key matches the expected format on the server side
				{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
			);
		} catch (error) {
			console.error('Failed to bookmark article: ' + error);
		}
	}
} satisfies Actions;

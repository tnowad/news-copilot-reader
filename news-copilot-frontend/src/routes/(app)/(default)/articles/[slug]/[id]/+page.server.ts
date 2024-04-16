import type { Actions, PageServerLoad } from './$types';
import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import commentsService from '$lib/services/comment.service';
import viewService from '$lib/services/view.service';
import bookmarksService from '$lib/services/bookmark.service';
export const load: PageServerLoad = async ({ params, locals, cookies }) => {
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

	const bookmarkResponse = await bookmarksService.getBookmarks(
		{
			articleId: id,
			userId: locals.user?.id ?? 0,
			limit: 1
		},
		{ Authorization: `Bearer ${cookies.get('accessToken')}` }
	);

	const article =
		articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.article : null;
	const comments =
		commentsResponse.statusCode === StatusCodes.OK ? commentsResponse.data.comments : [];
	const bookmark =
		bookmarkResponse.statusCode === StatusCodes.OK && bookmarkResponse.data.bookmarks.length > 0
			? bookmarkResponse.data.bookmarks[0]
			: null;

	return {
		article,
		comments,
		bookmark,
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

		return commentsResponse;

		console.log(commentsResponse);
	},
	markViewed: async (event) => {
		const articleId = parseInt(event.params.id);
		await viewService.markArticleViewed(
			{ articleId: articleId },
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);
	},
	createBookmark: async (event) => {
		try {
			const articleId = parseInt(event.params.id);
			const userId = event.locals.user?.id;

			const bookmarkResponse = await bookmarksService.createBookmark(
				{ articleId: articleId, userId: userId },
				{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
			);

			return bookmarkResponse;
		} catch (error) {
			console.error('Failed to bookmark article: ' + error);
		}
	},
	deleteBookmark: async (event) => {
		try {
			const formData = await event.request.formData();
			const id = formData.get('bookmarkId') as unknown as number;
			const bookmarkResponse = await bookmarksService.deleteBookmark(
				{ id },
				{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
			);
			return bookmarkResponse;
		} catch (error) {
			console.error('Failed to delete bookmark: ' + error);
		}
	}
} satisfies Actions;

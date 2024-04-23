import type { Actions, PageServerLoad } from './$types';
import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import commentsService from '$lib/services/comment.service';
import viewService from '$lib/services/view.service';
import reportService from '$lib/services/report.service';
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
		limit: 4,
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
	},
	updateComment: async (event) => {
		const formData = await event.request.formData();
		if (!event.locals.user) {
			return;
		}
		const commendId = formData.get('commentId') as unknown as number;
		const content = formData.get('content') as string;

		const commentResponse = await commentsService.updateComment(
			{
				id: commendId,
				content: content
			},
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);

		return commentResponse;
	},
	deleteComment: async (event) => {
		const formData = await event.request.formData();
		if (!event.locals.user) {
			return;
		}
		const commentId = formData.get('commentId') as unknown as number;

		const commentResponse = await commentsService.deleteComment(
			{ id: commentId },
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);

		return commentResponse;
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
			console.log('Creating');
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
	},
	createArticleReport: async (event) => {
		console.log('Creating');
		const formData = await event.request.formData();
		const content = formData.get('reportArticleContent') as string;
		const id = parseInt(event.params.id);
		console.log(content, id);
		const reportRespone = await reportService.createReport({
			content: content,
			objectId: id,
			objectType: 'Article'
		});
		console.log(reportRespone);
		return;
	},
	createCommentReport: async (event) => {
		console.log('Creating');
		const formData = await event.request.formData();
		const content = formData.get('reportCommentContent') as string;
		const id = formData.get('reportCommentId') as unknown as number;
		console.log(content, id);
		const reportRespone = await reportService.createReport({
			content: content,
			objectId: id,
			objectType: 'Comment'
		});
		console.log(reportRespone);
		return;
	},
	updateArticleReport: async (event) => {
		console.log('Creating');
		const formData = await event.request.formData();
		const content = formData.get('reportArticleContent') as string;
		const id = parseInt(event.params.id);
		console.log(content, id);
		const reportRespone = await reportService.updateReport({ content: content, reportId: id });
		console.log(reportRespone);
		return;
	}
} satisfies Actions;

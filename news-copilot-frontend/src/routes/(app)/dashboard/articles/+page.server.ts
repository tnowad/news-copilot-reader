import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import type { Actions, PageServerLoad } from './$types';

export const load = async (event) => {
	const page = parseInt(event.url.searchParams.get('page') ?? 1);
	const limit = parseInt(event.url.searchParams.get('limit') ?? 10);
	const search = event.url.searchParams.get('search') ?? '';

	const articlesResponse = await articleService.getAllArticles({
		includes: ['author', 'categories'],
		page: page,
		limit: limit,
		search: search
	});

	return {
		articles: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.articles : [],
		metadata: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.metadata : null
	};
};

export const actions = {
	deleteArticle: async (event) => {
		if (!event.locals.user) {
			return;
		}

		const formData = await event.request.formData();
		const articleId = formData.get('articleId') as unknown as number;

		const deleteArticleResponse = await articleService.deleteArticle(
			{
				id: articleId
			},
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);

		console.log(deleteArticleResponse);
		return deleteArticleResponse;
	}
} satisfies Actions;

import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';

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

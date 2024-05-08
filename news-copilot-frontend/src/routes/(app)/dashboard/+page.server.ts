import statisticsService from '$lib/services/statistic.service';
import { StatusCodes } from 'http-status-codes';
import articleService from '$lib/services/article.service';
import type { Actions, PageServerLoad } from './$types';

export const load = async (event) => {
	const articlesStatisticsResponse = await statisticsService.getArticlesStatistics();
	const getCategoryArticleCountResponse = await statisticsService.getCategoryArticleCount();

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
		articlesStatistics:
			articlesStatisticsResponse.statusCode === StatusCodes.OK
				? articlesStatisticsResponse.data
				: null,
		categoryArticleCount:
			getCategoryArticleCountResponse.statusCode === StatusCodes.OK
				? getCategoryArticleCountResponse.data
				: null,
		articles: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.articles : [],
		metadata: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.metadata : null
	};
};

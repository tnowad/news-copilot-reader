import statisticsService from '$lib/services/statistic.service';
import { StatusCodes } from 'http-status-codes';

export const load = async (event) => {
	const articlesStatisticsResponse = await statisticsService.getArticlesStatistics();
	const getCategoryArticleCountResponse = await statisticsService.getCategoryArticleCount();

	return {
		articlesStatistics:
			articlesStatisticsResponse.statusCode === StatusCodes.OK
				? articlesStatisticsResponse.data
				: null,
		categoryArticleCount:
			getCategoryArticleCountResponse.statusCode === StatusCodes.OK
				? getCategoryArticleCountResponse.data
				: null
	};
};

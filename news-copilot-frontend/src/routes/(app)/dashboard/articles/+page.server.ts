import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';

export const load = async () => {
	const articlesResponse = await articleService.getAllArticles({});

	return {
		articles: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.articles : [],
		metadata: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.metadata : {}
	};
};

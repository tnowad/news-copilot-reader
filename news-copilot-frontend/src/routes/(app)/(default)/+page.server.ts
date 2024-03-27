import artcileService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const articlesResponse = await artcileService.getAllArticles({ sortBy: 'created_at', sortOrder: 'desc', })
	const articles = articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.articles : []
	const latestArticle = articles.slice(0, 12)
	const hotArticles = articles.slice(0, 12)
	const recommendedArticle = articles.slice(0, 12)
	
	return {
		latestArticle
	};
};

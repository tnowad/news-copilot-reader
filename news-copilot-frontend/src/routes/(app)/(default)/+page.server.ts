import artcileService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import type { PageServerLoad } from './$types';
import categoryService from '$lib/services/category.service';

export const load: PageServerLoad = async (event) => {
	const articlesResponse = await artcileService.getAllArticles({ sortBy: 'created_at', sortOrder: 'desc', })
	const articles = articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.articles : []
	const latestArticle = articles.slice(0, 12)
	const hotArticles = articles.slice(0, 12)
	const recommendedArticle = articles.slice(0, 12)
	const categoriesResponse =await  categoryService.getAllCategories({limit:10})
	
	const categories = categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : []

	return {
		latestArticle,
		categories
	};
};

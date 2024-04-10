import articleService from '$lib/services/article.service';
import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	try {
		const [
			latestArticleResponse,
			hotArticlesResponse,
			categoriesResponse,
			recommendArticlesResponse
		] = await Promise.all([
			articleService.getAllArticles({
				sortBy: 'createdAt',
				sortOrder: 'desc',
				includes: ['author', 'categories'],
				limit: 12
			}),
			articleService.getAllArticles({
				sortBy: 'viewCount',
				sortOrder: 'desc',
				includes: ['author', 'categories'],
				limit: 12
			}),
			categoryService.getAllCategories({ limit: 10 }),
			articleService.getRecommendArticles({ userId: event.locals.user?.id, limit: 5 })
		]);

		const latestArticles =
			latestArticleResponse.statusCode === StatusCodes.OK
				? latestArticleResponse.data.articles
				: [];

		const hotArticles =
			hotArticlesResponse.statusCode === StatusCodes.OK ? hotArticlesResponse.data.articles : [];
		const categories =
			categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : [];
		const recommendArticles =
			recommendArticlesResponse.statusCode === StatusCodes.OK
				? recommendArticlesResponse.data.articles
				: [];

		return { latestArticles, hotArticles, categories, recommendArticles };
	} catch (error) {
		console.error('Error occurred while loading data:', error);
		return { latestArticles: [], hotArticles: [], categories: [] };
	}
};

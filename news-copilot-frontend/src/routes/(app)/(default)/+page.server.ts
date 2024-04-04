import articleService from '$lib/services/article.service';
import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	try {
		const [latestArticleResponse, hotArticlesResponse, categoriesResponse] = await Promise.all([
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
			categoryService.getAllCategories({ limit: 10 })
		]);

		const latestArticles =
			latestArticleResponse.statusCode === StatusCodes.OK
				? latestArticleResponse.data.articles
				: [];
		console.log(latestArticles);
		const hotArticles =
			hotArticlesResponse.statusCode === StatusCodes.OK ? hotArticlesResponse.data.articles : [];
		const categories =
			categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : [];

		return { latestArticles, hotArticles, categories };
	} catch (error) {
		console.error('Error occurred while loading data:', error);
		return { latestArticles: [], hotArticles: [], categories: [] };
	}
};

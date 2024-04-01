import type { PageServerLoad } from './$types';
import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';
import artcileService from '$lib/services/article.service';

export const load: PageServerLoad = async (event) => {
	const { id } = event.params;
	const categoryResponse = await categoryService.getCategoryById({
		id: parseInt(id),
		style: 'full'
	});

	const articlesResponse = await artcileService.getAllArticles({
		limit: 12,
		includes: ['categories', 'author'],
		sortBy: 'publishedAt',
		sortOrder: 'desc'
		// filters: {
		// 	categories: [id]
		// }
	});
	const category =
		categoryResponse.statusCode === StatusCodes.OK ? categoryResponse.data.category : null;
	return {
		category,
		articles: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.articles : [],
		metadata: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.metadata : []
	};
};

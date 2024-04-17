import type { Actions } from '@sveltejs/kit';
import artcileService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import type { PageServerLoad } from './$types';
import categoryService from '$lib/services/category.service';

export const load: PageServerLoad = async (event) => {
	const searchInput = event.url.searchParams.get('search') ?? '';
	const categoryIds = event.url.searchParams.getAll('category') as unknown[] as number[];

	const articleResponse = await artcileService.getAllArticles({
		search: searchInput,
		categoryIds,
		includes: ['author', 'categories'],
		limit: 24
	});

	const categoriesResponse = await categoryService.getAllCategories({
		limit: 100
	});
	const articles =
		articleResponse.statusCode === StatusCodes.OK ? articleResponse.data.articles : [];
	const metadata =
		articleResponse.statusCode === StatusCodes.OK ? articleResponse.data.metadata : null;
	const categories =
		categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : [];
	return { articles, categories, metadata };
};

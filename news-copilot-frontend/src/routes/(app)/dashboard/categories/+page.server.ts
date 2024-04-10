import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';

export const load = async (event) => {
	const page = parseInt(event.url.searchParams.get('page') ?? 1);
	const limit = parseInt(event.url.searchParams.get('limit') ?? 10);
	const search = event.url.searchParams.get('search') ?? '';

	const categoriesResponse = await categoryService.getAllCategories({
		includes: ['description'],
		page: page,
		limit: limit,
		search: search

	});

	return {
		categories:
			categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : [],
		metadata:
			categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.metadata : null
	};
};

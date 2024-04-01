import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';

export const load = async (event) => {
	const categoriesResponse = await categoryService.getAllCategories({
		limit: 100,
		style: 'compact',
		sortBy: 'title'
	});

	return {
		categories:
			categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : [],
		user: event.locals.user
	};
};

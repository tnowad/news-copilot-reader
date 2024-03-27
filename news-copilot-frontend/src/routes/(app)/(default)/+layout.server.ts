import type { LayoutServerLoad } from './$types';
import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';
export const load: LayoutServerLoad = async (event) => {
	const categoriesResponse = await categoryService.getAllCategories({});
	const categoryItems =
		categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : [];

	return {
		categoryItems,
		user: event.locals.user
	};
};

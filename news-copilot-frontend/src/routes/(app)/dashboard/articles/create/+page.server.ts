import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';

export const ssr = false;

export const load = async () => {
	const categoriesResponse = await categoryService.getAllCategories({});

	return {
		categories:
			categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : []
	};
};

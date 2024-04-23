import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';
import type { Actions, PageServerLoad } from './$types';

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

export const actions = {
	deleteCategory: async (event) => {
		if (!event.locals.user) {
			return;
		}

		const formData = await event.request.formData();
		const categoryId = formData.get('categoryId') as unknown as number;

		console.log(categoryId);
		const deleteCategoryResponse = await categoryService.deleteCategory(
			{
				id: categoryId
			},
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);

		return deleteCategoryResponse;
	}
} satisfies Actions;

import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';
import userService from '$lib/services/user.service';
export const ssr = false;

export const load = async (event) => {
	const categoriesResponse = await categoryService.getAllCategories({
		limit: 100,
		style: 'compact',
		sortBy: 'title'
	});

	const [categoriesResponse, usersResponse] = await Promise.all([
		categoryService.getAllCategories({}),
		userService.getCurrentUserProfile()
	]);
	const currentUser = usersResponse.statusCode === StatusCodes.OK ? usersResponse.data.user : null;
	const categories = categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : [];
	return {
		categories:
			categoriesResponse.statusCode === StatusCodes.OK ? categoriesResponse.data.categories : [],
		user: event.locals.user
	};
};

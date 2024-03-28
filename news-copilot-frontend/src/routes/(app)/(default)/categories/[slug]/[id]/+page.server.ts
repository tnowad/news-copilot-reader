import type { PageServerLoad } from './$types';
import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';

export const load: PageServerLoad = async (event) => {
	const { id } = event.params;
	const categoryResponse = await categoryService.getCategoryById({ id: parseInt(id) });
	const category =
		categoryResponse.status === StatusCodes.OK ? categoryResponse.data.category : null;
	return { category };
};

import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';
import type { Actions } from '../$types';
import type { PageServerLoad } from '../$types';
import artcileService from '$lib/services/article.service';

export const load: PageServerLoad = async (event) => {
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
export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		if (!event.locals.user) {
			return;
		}
		const articleTitle = formData.get('title') as string;
		const authorId = event.locals.user.id;
		const summary = formData.get('summary') as string;
		const category = formData.getAll('category') as unknown as number[];
		const coverImage = formData.get('coverImage') as string;
		const content = formData.get('content') as string;

		const articleResponse = await artcileService.createArticle(
			{
				title: articleTitle,
				summary: summary,
				coverImage: coverImage,
				content: content,
				authorId: authorId,
				categoryIds: category
			},
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);

		return articleResponse;
	}
} satisfies Actions;

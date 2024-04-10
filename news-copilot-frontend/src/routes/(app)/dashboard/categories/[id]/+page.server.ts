import categoryService from '$lib/services/category.service';
import { StatusCodes } from 'http-status-codes';
import artcileService from '$lib/services/article.service';
import type { PageServerLoad } from '../../../(default)/categories/[slug]/[id]/$types';
import type { Actions } from './$types';

export const load: PageServerLoad = async (event: any) => {
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



export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		if (!event.locals.user) {
			return;
		}

		const categoriesTitle = formData.get('title') as string;
		const categoriesSlug = formData.get('slug') as string;
		const despriction = formData.get('description') as string;
		const categoryId = event.params.id as unknown as number;

		const categoriesResponse = await categoryService.updateCategory({
			id: categoryId,
			slug: categoriesSlug,
			title: categoriesTitle,
			description: despriction
		}, { Authorization: `Bearer ${event.cookies.get('accessToken')}` }

		);

		console.log(categoriesResponse)

	}
} satisfies Actions;

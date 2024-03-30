import type { PageServerLoad } from './$types';
import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';

export const load: PageServerLoad = async ({ params }) => {
	const id = parseInt(params.id);

	const articlesResponse = await articleService.getArticleById({
		id: id,
		includes: ['author', 'categories', 'comments'],
		style: 'full'
	});

	return {
		article: articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.article : null
	};
};

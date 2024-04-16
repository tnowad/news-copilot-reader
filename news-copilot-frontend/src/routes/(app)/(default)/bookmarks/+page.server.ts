import type { Actions } from '@sveltejs/kit';
import artcileService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';
import type { PageServerLoad } from '../$types';

export const load: PageServerLoad = async (event) => {
	const articleResponse = await artcileService.getAllBookmarkedArticles(
		{
			includes: ['author', 'categories']
		},
		{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
	);
	const articles =
		articleResponse.statusCode === StatusCodes.OK ? articleResponse.data.articles : [];
	return { articles };
};

export const actions = {
	default: async (event) => {
		const articleResponse = await artcileService.getAllArticles({ limit: 24 });
		const articles =
			articleResponse.statusCode === StatusCodes.OK ? articleResponse.data.articles : [];
		return articles;
	}
} satisfies Actions;

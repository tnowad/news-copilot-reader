import type { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
import type { Article } from './types';

type CreateArticleBody = {
	title: string;
	summary: string;
	coverImage?: string;
	content: string;
	authorId?: number;
	categoryIds: number[];
};

type CreateArticleSuccessful = {
	statusCode: StatusCodes.CREATED;
	data: {
		article: Article;
	};
	message: string;
};

type CreateArticleValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field: 'title' | 'summary' | 'content' | 'authorId' | 'categoryIds';
		message: string;
	}[];
};

type CreateArticlePermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

type CreateArticleServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type CreateArticleResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| CreateArticleSuccessful
		| CreateArticlePermissionDenied
		| CreateArticleValidationFailed
		| CreateArticleServerError
	>;
};

const createArticle = async (body: CreateArticleBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/articles', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as CreateArticleResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to sign in: ' + (error as Error).message);
	}
};

type UpdateArticleBody = {
	id: number;
	title?: string;
	summary?: string;
	coverImage?: string;
	content?: string;
	authorId?: number;
	categoryIds?: number[];
};

type UpdateArticleSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		article: Article;
	};
	message: string;
};

type UpdateArticleValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field: 'id' | 'title' | 'summary' | 'content' | 'authorId' | 'categoryIds';
		message: string;
	}[];
};

type UpdateArticlePermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

type UpdateArticleNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type UpdateArticleServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type UpdateArticleResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| UpdateArticleSuccessful
		| UpdateArticlePermissionDenied
		| UpdateArticleValidationFailed
		| UpdateArticleNotFound
		| UpdateArticleServerError
	>;
};

const updateArticle = async (body: UpdateArticleBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/articles/${body.id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'PUT',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as UpdateArticleResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to update article: ' + (error as Error).message);
	}
};

type DeleteArticleParams = {
	id: number;
};

type DeleteArticleSuccessful = {
	statusCode: StatusCodes.NO_CONTENT;
	message: string;
};

type DeleteArticlePermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

type DeleteArticleNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type DeleteArticleServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type DeleteArticleResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| DeleteArticleSuccessful
		| DeleteArticlePermissionDenied
		| DeleteArticleNotFound
		| DeleteArticleServerError
	>;
};

const deleteArticle = async (params: DeleteArticleParams, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/articles/${params.id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'DELETE',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as DeleteArticleResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to delete article: ' + (error as Error).message);
	}
};

type GetArticleByIdParams = {
	id: number;
	includes?: ('author' | 'categories' | 'comments')[];
	style?: 'compact' | 'full';
};

type GetArticleByIdSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		article: Article;
	};
	message: string;
};

type GetArticleByIdNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type GetArticleByIdServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetArticleByIdResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		GetArticleByIdSuccessful | GetArticleByIdNotFound | GetArticleByIdServerError
	>;
};

const getArticleById = async (params: GetArticleByIdParams, headers: HeadersInit = {}) => {
	try {
		const { id, includes, style } = params;
		const url = new URL(`/articles/${id}`, API_URL);
		const queryParams = new URLSearchParams();

		if (includes) {
			includes.forEach((param) => queryParams.append('includes', param));
		}

		if (style) {
			queryParams.set('style', style);
		}

		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetArticleByIdResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to get article by ID: ' + (error as Error).message);
	}
};

type GetAllArticlesParams = {
	page?: number;
	limit?: number;
	search?: string;
	categoryIds?: number[];
	sortBy?: 'title' | 'createdAt' | 'viewCount' | 'publishedAt' | 'updatedAt';
	sortOrder?: 'asc' | 'desc';
	style?: 'compact' | 'full';
	includes?: ('author' | 'categories')[];
};

type GetAllArticlesSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		articles: Article[];
		metadata: {
			pagination: {
				offset: number;
				limit: number;
				previousOffset: number;
				nextOffset: number;
				currentPage: number;
				pageCount: number;
				totalCount: number;
			};
			sortedBy: {
				name: 'title' | 'date';
				order: 'asc' | 'desc';
			};
			style: 'compact' | 'full';
			filters: {
				search: string;
				categoryIds: number[];
			};
		};
	};
	message: string;
};

type GetAllArticlesServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetAllArticlesResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetAllArticlesSuccessful | GetAllArticlesServerError>;
};

const getAllArticles = async (params: GetAllArticlesParams = {}, headers: HeadersInit = {}) => {
	try {
		const { page, limit, search, categoryIds, sortBy, sortOrder, style, includes } = params;
		const url = new URL('/articles', API_URL);
		const queryParams = new URLSearchParams();

		if (page) queryParams.set('page', page.toString());
		if (limit) queryParams.set('limit', limit.toString());
		if (search) queryParams.set('search', search);
		if (categoryIds) categoryIds.forEach((id) => queryParams.append('categoryIds', id.toString()));
		if (sortBy) queryParams.set('sortBy', sortBy);
		if (sortOrder) queryParams.set('sortOrder', sortOrder);
		if (style) queryParams.set('style', style);
		if (includes) includes.forEach((param) => queryParams.append('includes', param));

		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetAllArticlesResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch articles: ' + (error as Error).message);
	}
};

type GetRecommendArticlesParams = {
	limit?: number;
	articleId?: number;
	userId?: number;
	style?: 'compact' | 'full';
	includes?: ('author' | 'categories')[];
};

type GetRecommendArticlesSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		articles: Article[];
		metadata: {
			pagination: {
				offset: number;
				limit: number;
				previousOffset: number;
				nextOffset: number;
				currentPage: number;
				pageCount: number;
				totalCount: number;
			};
			sortedBy: {
				name: 'title' | 'date';
				order: 'asc' | 'desc';
			};
			style: 'compact' | 'full';
			filters: {
				search: string;
				categoryIds: number[];
			};
		};
	};
	message: string;
};

type GetRecommendArticlesServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetRecommendArticlesResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetRecommendArticlesSuccessful | GetRecommendArticlesServerError>;
};

const getRecommendArticles = async (
	params: GetRecommendArticlesParams = {},
	headers: HeadersInit = {}
) => {
	try {
		const { limit, userId, articleId, style, includes } = params;
		const url = new URL('/recommendations/articles', API_URL);
		const queryParams = new URLSearchParams();

		if (articleId) queryParams.set('articleId', articleId.toString());
		if (userId) queryParams.set('userId', userId.toString());
		if (limit) queryParams.set('limit', limit.toString());
		if (style) queryParams.set('style', style);

		if (includes) includes.forEach((param) => queryParams.append('includes', param));

		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetRecommendArticlesResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch articles: ' + (error as Error).message);
	}
};

type getAllBookmarkedArticlesParams = {
	page?: number;
	limit?: number;
	sortBy?: 'title' | 'createdAt' | 'viewCount' | 'publishedAt' | 'updatedAt';
	sortOrder?: 'asc' | 'desc';
	style?: 'compact' | 'full';
	includes?: ('author' | 'categories')[];
};

type GetAllBookmarkedArticlesSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		articles: Article[];
		metadata: {
			pagination: {
				offset: number;
				limit: number;
				previousOffset: number;
				nextOffset: number;
				currentPage: number;
				pageCount: number;
				totalCount: number;
			};
			sortedBy: {
				name: 'title' | 'date';
				order: 'asc' | 'desc';
			};
			style: 'compact' | 'full';
		};
	};
	message: string;
};

type GetAllBookmarkedArticlesServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetAllBookmarkedArticlesResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetAllBookmarkedArticlesSuccessful | GetAllBookmarkedArticlesServerError>;
};

const getAllBookmarkedArticles = async (
	params: getAllBookmarkedArticlesParams = {},
	headers: HeadersInit = {}
) => {
	try {
		const { page, limit, sortBy, sortOrder, style, includes } = params;
		const url = new URL('/articles/bookmarks', API_URL);
		const queryParams = new URLSearchParams();

		if (page) queryParams.set('page', page.toString());
		if (limit) queryParams.set('limit', limit.toString());
		if (sortBy) queryParams.set('sortBy', sortBy);
		if (sortOrder) queryParams.set('sortOrder', sortOrder);
		if (style) queryParams.set('style', style);
		if (includes) includes.forEach((param) => queryParams.append('includes', param));

		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetAllBookmarkedArticlesResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch articles: ' + (error as Error).message);
	}
};

const artcileService = {
	createArticle,
	updateArticle,
	deleteArticle,
	getArticleById,
	getAllArticles,
	getRecommendArticles,
	getAllBookmarkedArticles
};

export default artcileService;

import { API_URL } from '$env/static/private';
import type { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import type { Category } from './types';

type CreateCategoryBody = {
	title: string;
	slug: string;
	description?: string;
};

type CreateCategorySuccessful = {
	statusCode: StatusCodes.CREATED;
	data: {
		category: Category;
	};
	message: string;
};

type CreateCategoryValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field: 'title' | 'slug' | 'description';
		message: string;
	}[];
};

type CreateCategoryPermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

type CreateCategoryServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type CreateCategoryResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| CreateCategorySuccessful
		| CreateCategoryPermissionDenied
		| CreateCategoryValidationFailed
		| CreateCategoryServerError
	>;
};

const createCategory = async (body: CreateCategoryBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/categories', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as CreateCategoryResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to create category: ' + (error as Error).message);
	}
};

type UpdateCategoryBody = {
	id: number;
	title?: string;
	slug?: string;
	description?: string;
};

type UpdateCategorySuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		category: Category;
	};
	message: string;
};

type UpdateCategoryValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field: 'id' | 'title' | 'slug' | 'description';
		message: string;
	}[];
};

type UpdateCategoryPermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

type UpdateCategoryNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type UpdateCategoryServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type UpdateCategoryResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| UpdateCategorySuccessful
		| UpdateCategoryPermissionDenied
		| UpdateCategoryValidationFailed
		| UpdateCategoryNotFound
		| UpdateCategoryServerError
	>;
};

const updateCategory = async (body: UpdateCategoryBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/categories/${body.id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'PUT',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as UpdateCategoryResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to update category: ' + (error as Error).message);
	}
};

type DeleteCategoryParams = {
	id: number;
};

type DeleteCategorySuccessful = {
	statusCode: StatusCodes.NO_CONTENT;
	message: string;
};

type DeleteCategoryPermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

type DeleteCategoryNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type DeleteCategoryServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type DeleteCategoryResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| DeleteCategorySuccessful
		| DeleteCategoryPermissionDenied
		| DeleteCategoryNotFound
		| DeleteCategoryServerError
	>;
};

const deleteCategory = async (params: DeleteCategoryParams, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/categories/${params.id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'DELETE',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as DeleteCategoryResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to delete category: ' + (error as Error).message);
	}
};

type GetCategoryByIdParams = {
	id: number;
	includes?: 'description'[];
	style?: 'compact' | 'full';
};

type GetCategoryByIdSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		category: Category;
	};
	message: string;
};

type GetCategoryByIdNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type GetCategoryByIdServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetCategoryByIdResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		GetCategoryByIdSuccessful | GetCategoryByIdNotFound | GetCategoryByIdServerError
	>;
};

const getCategoryById = async (params: GetCategoryByIdParams, headers: HeadersInit = {}) => {
	try {
		const { id, includes, style } = params;
		const url = new URL(`/categories/${id}`, API_URL);
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

		const response = (await fetch(url, requestInit)) as GetCategoryByIdResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to get category by ID: ' + (error as Error).message);
	}
};

type GetAllCategoriesParams = {
	page?: number;
	limit?: number;
	search?: string;
	includes?: 'description'[];
	sortBy?: 'title' | 'slug';
	sortOrder?: 'asc' | 'desc';
	style?: 'compact' | 'full';
};

type GetAllCategoriesSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		categories: Category[];
		metadata: {
			pagination: {
				offset: number;
				limit: number;
				previousOffset: number | null;
				nextOffset: number | null;
				currentPage: number;
				pageCount: number;
				totalCount: number;
			};
			sortedBy: {
				name: 'title' | 'slug';
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

type GetAllCategoriesServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetAllCategoriesResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetAllCategoriesSuccessful | GetAllCategoriesServerError>;
};

const getAllCategories = async (params: GetAllCategoriesParams = {}, headers: HeadersInit = {}) => {
	try {
		const { page, limit, search, includes, sortBy, sortOrder, style } = params;
		const url = new URL('/categories', API_URL);
		const queryParams = new URLSearchParams();

		if (page) queryParams.set('page', page.toString());
		if (limit) queryParams.set('limit', limit.toString());
		if (search) queryParams.set('search', search);
		if (includes) includes.forEach((param) => queryParams.append('includes', param));
		if (sortBy) queryParams.set('sortBy', sortBy);
		if (sortOrder) queryParams.set('sortOrder', sortOrder);
		if (style) queryParams.set('style', style);

		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetAllCategoriesResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch categories: ' + (error as Error).message);
	}
};
const categoryService = {
	createCategory,
	updateCategory,
	deleteCategory,
	getCategoryById,
	getAllCategories
};

export default categoryService;

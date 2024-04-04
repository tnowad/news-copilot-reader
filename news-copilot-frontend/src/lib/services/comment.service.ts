import type { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
type CreateCommentBody = {
	content: string;
	authorId: number;
	articleId: number;
};
type CreateCommentSuccessful = {
	statuscode: StatusCodes.CREATED;
	data: {
		id: number;
		content: string;
		createdAt: string;
		updatedAt: string;
		author: {
			id: number;
			displayName: string;
			avatarImage: string;
		};
	};
	message: string;
};
type CreateCommentPermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};
type CreateCommentServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};
type CreateCommentValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field: 'content' | 'authorId' | 'articleId';
		message: string;
	}[];
};

type CreateCommentResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| CreateCommentSuccessful
		| CreateCommentPermissionDenied
		| CreateCommentValidationFailed
		| CreateCommentServerError
	>;
};

const createComment = async (body: CreateCommentBody, headers: HeadersInit = {}) => {
	const url = new URL('/comments', API_URL);
	const requestInit: RequestInit = {
		method: 'POST',
		body: JSON.stringify(body),
		headers: { ...defaultHeaders, ...headers }
	};
	const response = (await fetch(url, requestInit)) as CreateCommentResponse;
	return response.json();
};

type GetAllCommentSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		comments: {
			id: number;
			content: string;
			createdAt: string;
			updatedAt: string;
			articleID: number;
			author: {
				id: number;
				displayName: string;
				avatarImage: string;
			};
		}[];
		metadata: {
			pagination: {
				offset: number;
				limit: number;
				previousOffset: number;
				nextOffset: number;
				currentPage: number;
				totalCount: number;
			};
			sortedBy: {
				name: 'date' | 'name';
				sortOrder: 'asc' | 'desc';
			};
			filter: {
				articleId: string;
				userId: string;
				parentId: string;
				search: string;
			};
		};
		message: string;
	};
};
type GetAllCommentsServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};
type GetAllCommentsParams = {
	page?: number;
	search?: string;
	articleId?: number;
	limit?: number;
	sortBy?: 'name' | 'title';
	sortOrder?: 'asc' | 'desc';
	style?: 'full';
	includes?: 'author'[];
};
type GetAllCommentsRespone = Omit<Response, 'json'> & {
	json: () => Promise<GetAllCommentSuccessful | GetAllCommentsServerError>;
};
const getAllComments = async (params: GetAllCommentsParams = {}, headers: HeadersInit = {}) => {
	try {
		const {
			page,
			limit,
			search,
			sortBy,
			sortOrder,
			style,
			includes,
			articleId: articleID
		} = params;
		const url = new URL('/comments', API_URL);
		const queryParams = new URLSearchParams();
		if (page) queryParams.set('page', page.toString());
		if (limit) queryParams.set('limit', limit.toString());
		if (search) queryParams.set('search', search);
		if (sortBy) queryParams.set('sortBy', sortBy);
		if (sortOrder) queryParams.set('sortOrder', sortOrder);
		if (style) queryParams.set('style', style);
		if (articleID) queryParams.set('articleId', articleID.toString());
		if (includes) includes.forEach((param) => queryParams.append('includes', param));

		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetAllCommentsRespone;

		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch articles: ' + (error as Error).message);
	}
};
type GetCommentByArticleIDServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};
type UpdateCommentBody = {
	id: number;
	content?: string;
	authorId?: number;
	articleId?: number;
};

type UpdateCommentSuccessful = {
	statusCode: StatusCodes.OK;
	message: string;
	data: {
		comment: {
			id: number;
			content: string;
			createdAt: string;
			updatedAt: string;
			articleId: number;
			author: {
				id: number;
				displayName: string;
				avatarImage: string;
			};
		};
	};
};

type UpdateCommentNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type UpdateCommentResponse = Omit<Response, 'json'> & {
	json: () => Promise<UpdateCommentSuccessful | UpdateCommentNotFound>;
};

const updateComment = async (body: UpdateCommentBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/comments/${body.id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'PUT',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as UpdateCommentResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to update comment: ' + (error as Error).message);
	}
};

type DeleteCommentParams = {
	id: number;
};

type DeleteCommentSuccessful = {
	statusCode: StatusCodes.NO_CONTENT;
	message: string;
};

type DeleteCommentNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type DeleteCommentResponse = Omit<Response, 'json'> & {
	json: () => Promise<DeleteCommentSuccessful | DeleteCommentNotFound>;
};

const deleteComment = async (params: DeleteCommentParams, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/comments/${params.id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'DELETE',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as DeleteCommentResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to delete comment: ' + (error as Error).message);
	}
};

type GetCommentByIdParams = {
	id: number;
};

type GetCommentByIdSuccessful = {
	statusCode: StatusCodes.OK;
	message: string;
	data: {
		comment: {
			id: number;
			content: string;
			createdAt: string;
			updatedAt: string;
			articleId: number;
			author: {
				id: number;
				displayName: string;
				avatarImage: string;
			};
		};
	};
};

type GetCommentByIdNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type GetCommentByIdResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetCommentByIdSuccessful | GetCommentByIdNotFound>;
};

const getCommentById = async (params: GetCommentByIdParams, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/comments/${params.id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetCommentByIdResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to get comment by ID: ' + (error as Error).message);
	}
};

const commentServerices = {
	getAllComments,
	createComment,
	updateComment,
	deleteComment,
	getCommentById
};

export default commentServerices;

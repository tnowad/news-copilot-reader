import { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
import type { Bookmark } from './types';

type CreateBookmarkBody = {
	userId?: number;
	articleId?: number;
};

type CreateBookmarkSuccessful = {
	statusCode: StatusCodes.CREATED;
	data: {
		bookmark: Bookmark;
	};
	message: string;
};

type CreateBookmarkServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type CreateBookmarkResponse = Omit<Response, 'json'> & {
	json: () => Promise<CreateBookmarkSuccessful | CreateBookmarkServerError>;
};

const createBookmark = async (body: CreateBookmarkBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/bookmarks', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as CreateBookmarkResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to create bookmark: ' + (error as Error).message);
	}
};

type DeleteBookmarkParams = {
	id: number;
};

type DeleteBookmarkSuccessful = {
	statusCode: StatusCodes.NO_CONTENT;
	message: string;
};

type DeleteBookmarkServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type DeleteBookmarkResponse = Omit<Response, 'json'> & {
	json: () => Promise<DeleteBookmarkSuccessful | DeleteBookmarkServerError>;
};

const deleteBookmark = async (params: DeleteBookmarkParams, headers: HeadersInit = {}) => {
	try {
		const { id } = params;

		const url = new URL(`/bookmarks/${id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'DELETE',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as DeleteBookmarkResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to delete bookmark: ' + (error as Error).message);
	}
};

type GetBookmarksParams = {
	userId?: number;
	articleId?: number;
};

type GetBookmarksSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		bookmarks: Bookmark[];
	};
	message: string;
};

type GetBookmarksServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetBookmarksResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetBookmarksSuccessful | GetBookmarksServerError>;
};

const getBookmarks = async (params: GetBookmarksParams, headers: HeadersInit = {}) => {
	try {
		const { userId, articleId } = params;

		const url = new URL('/bookmarks', API_URL);
		userId && url.searchParams.append('userId', userId.toString());
		articleId && url.searchParams.append('articleId', articleId.toString());

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetBookmarksResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to get bookmarks: ' + (error as Error).message);
	}
};

type GetBookmarkByIdParams = {
	id: number;
};

type GetBookmarkByIdSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		bookmark: Bookmark;
	};
	message: string;
};

type GetBookmarkByIdNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type GetBookmarkByIdServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetBookmarkByIdResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		GetBookmarkByIdSuccessful | GetBookmarkByIdNotFound | GetBookmarkByIdServerError
	>;
};

const getBookmarkById = async (params: GetBookmarkByIdParams, headers: HeadersInit = {}) => {
	try {
		const { id } = params;
		const url = new URL(`/bookmarks/${id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetBookmarkByIdResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to get bookmark by ID: ' + (error as Error).message);
	}
};

const bookmarkService = {
	createBookmark,
	deleteBookmark,
	getBookmarkById,
	getBookmarks
};

export default bookmarkService;

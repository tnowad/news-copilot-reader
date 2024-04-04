import { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';

type CreateBookmarkBody = {
	article_id: number;
};

type CreateBookmarkSuccessful = {
	statusCode: StatusCodes.CREATED;
	message: string;
};

type CreateBookmarkArticleNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
};

type CreateBookmarkBookmarkExists = {
	statusCode: StatusCodes.BAD_REQUEST;
	message: string;
};

type CreateBookmarkResponse =
	| CreateBookmarkSuccessful
	| CreateBookmarkArticleNotFound
	| CreateBookmarkBookmarkExists;

const createBookmark = async (body: CreateBookmarkBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/bookmarks', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = await fetch(url, requestInit);

		if (response.ok) {
			return { statusCode: response.status, message: 'Bookmark created successfully' };
		} else if (response.status === StatusCodes.NOT_FOUND) {
			return { statusCode: response.status, message: 'Article not found' };
		} else if (response.status === StatusCodes.BAD_REQUEST) {
			return { statusCode: response.status, message: 'Bookmark already exists' };
		} else {
			throw new Error(`Failed to create bookmark: ${response.statusText}`);
		}
	} catch (error) {
		throw new Error('Failed to create bookmark: ' + (error as Error).message);
	}
};

type GetBookmarksSuccessful = {
	statusCode: StatusCodes.OK;
	bookmarks: {
		id: number;
		article_id: number;
		created_at: string;
	}[];
};

type GetBookmarksResponse = GetBookmarksSuccessful;

const getBookmarks = async (headers: HeadersInit = {}) => {
	try {
		const url = new URL('/bookmarks', API_URL);
		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = await fetch(url, requestInit);
		const data = await response.json();

		if (response.ok) {
			return { statusCode: response.status, bookmarks: data.bookmarks };
		} else {
			throw new Error(`Failed to get bookmarks: ${response.statusText}`);
		}
	} catch (error) {
		throw new Error('Failed to get bookmarks: ' + (error as Error).message);
	}
};

type DeleteBookmarkSuccessful = {
	statusCode: StatusCodes.OK;
	message: string;
};

type DeleteBookmarkNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
};

type DeleteBookmarkResponse = DeleteBookmarkSuccessful | DeleteBookmarkNotFound;

const deleteBookmark = async (bookmark_id: number, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/bookmarks/${bookmark_id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'DELETE',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = await fetch(url, requestInit);

		if (response.ok) {
			return { statusCode: response.status, message: 'Bookmark deleted successfully' };
		} else if (response.status === StatusCodes.NOT_FOUND) {
			return { statusCode: response.status, message: 'Bookmark not found' };
		} else {
			throw new Error(`Failed to delete bookmark: ${response.statusText}`);
		}
	} catch (error) {
		throw new Error('Failed to delete bookmark: ' + (error as Error).message);
	}
};

const bookmarkService = {
	createBookmark,
	getBookmarks,
	deleteBookmark
};

export default bookmarkService;

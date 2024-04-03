import type { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
type CreateCommentBody = {
	content: string
	authorId: number
	articleId: number
}
type CreateCommentSuccessful = {
	statuscode: StatusCodes.CREATED;
	data: {
		id: number;
		content: string,
		createdAt: string,
		updatedAt: string,
		author: {
			id: number,
			displayName: string,
			avatarImage: string
		};
	};
	message: string
}
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
	}
	const response = (await fetch(url, requestInit)) as CreateCommentResponse
	return response.json()
}



type GetAllCommentSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		comments: {
			id: number;
			content: string;
			createdAt: string;
			updatedAt: string;
			articleID : number;
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
	}
}
type GetAllCommentsServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
}
type GetAllCommentsParams = {
	page?: number;
	search?: string;
	articleId?: number;
	limit?: number;
	sortBy?: 'name' | 'title';
	sortOrder?: 'asc' | 'desc';
	style?: 'full',
	includes?: 'author'[]

}
type GetAllCommentsRespone = Omit<Response, 'json'> & {
	json: () => Promise<GetAllCommentSuccessful | GetAllCommentsServerError>;
}
const getAllComments = async (params: GetAllCommentsParams = {}, headers: HeadersInit = {}) => {
	try {
		const { page, limit, search, sortBy, sortOrder, style, includes , articleId: articleID } = params;
		const url = new URL('/comments', API_URL);
		const queryParams = new URLSearchParams();
		if (page) queryParams.set('page', page.toString());
		if (limit) queryParams.set('limit', limit.toString());
		if (search) queryParams.set('search', search);
		if (sortBy) queryParams.set('sortBy', sortBy);
		if (sortOrder) queryParams.set('sortOrder', sortOrder);
		if (style) queryParams.set('style', style);
		if (articleID) queryParams.set('articleID', articleID.toString());
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
}
type GetCommentByArticleIDServerError = {
	statusCode : StatusCodes.INTERNAL_SERVER_ERROR;
	message : string;
	error:string;
	
}

const commentServerices = {
	getAllComments,
	createComment
}
export default commentServerices;

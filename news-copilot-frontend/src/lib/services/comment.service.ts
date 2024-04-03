import type { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
type CreateCommentBody = {
	content: string
	author_id: number
	article_id: number
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
	statusCode: StatusCodes.ACCEPTED,
	data: {
		id: number,
		content: string,
		created_at: string,
		updated_at: string,
		author: {
			id: number,
			display_name: string,
			display_image: string
		};
	}[];
}





const commentServerices = {
	createComment
}
export default createComment

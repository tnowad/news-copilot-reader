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
		field:  'content' | 'authorId' | 'articleId';
		message: string;
	}[];
};

type CreateArticleResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| CreateCommentSuccessful
		| CreateCommentPermissionDenied
		| CreateCommentValidationFailed
		| CreateCommentServerError
	>;  
};


const createComment = async (body: CreateCommentBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/artciles', API_URL);
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


const commentServerices = async (body: CreateCommentBody, headers: HeadersInit = {}) => {
// createComment 
}


export default createComment





type DeleteCommentParams = {
	id: number;
};

type DeleteCommentSuccessful = {
	statusCode: StatusCodes.NO_CONTENT;
	message: string;
};

type DeleteCommentPermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

// type DeleteCommentNotFound = {
// 	statusCode: StatusCodes.NOT_FOUND;
// 	message: string;
// 	error: string;
// };

type DeleteCommentServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type DeleteCommentResponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| DeleteCommentSuccessful
		| DeleteCommentPermissionDenied
		// | DeleteCommentNotFound
		| DeleteCommentServerError
	>;
};

const deleteArticle = async (params: DeleteCommentParams, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/articles/${params.id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'DELETE',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as DeleteCommentResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to delete article: ' + (error as Error).message);
	}
};
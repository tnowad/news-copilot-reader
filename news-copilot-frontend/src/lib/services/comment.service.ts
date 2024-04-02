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

}


const commentServerices ={
createComment 


}
export default createComment
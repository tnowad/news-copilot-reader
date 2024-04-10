import { API_URL } from '$env/static/private';
import { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';

type MarkViewedBody = {
	articleId: number;
};
type MarkViewedResponse = {
	statusCode: StatusCodes.OK;
	message: string;
	data: {
		view: {
			articleId: number;
			userId: number;
			viewedAt: string;
		};
	};
};

type ErrorResponse = {
	statusCode: StatusCodes;
	message: string;
};

type MarkViewedError = ErrorResponse & {
	error: string;
};

type MarkViewedValidationFailed = ErrorResponse & {
	errors: {
		field: 'articleId';
		message: string;
	}[];
};

type ViewServiceResponse = Omit<Response, 'json'> & {
	json: () => Promise<MarkViewedResponse | MarkViewedError | MarkViewedValidationFailed>;
};

const markArticleViewed = async (
	body: MarkViewedBody,
	headers: HeadersInit = {}
): Promise<ViewServiceResponse> => {
	try {
		const { articleId } = body;
		const url = new URL(`/articles/${articleId}/mark-viewed`, API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json', ...defaultHeaders, ...headers }
		};

		const response = await fetch(url.toString(), requestInit);

		return response as ViewServiceResponse;
	} catch (error) {
		console.error('Failed to mark article as viewed:', error);
		throw new Error('Failed to mark article as viewed');
	}
};

const viewService = {
	markArticleViewed
};

export default viewService;

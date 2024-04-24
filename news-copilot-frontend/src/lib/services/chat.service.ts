import { API_URL } from '$env/static/private';
import type { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';

type CreateMessageBody = {
	message?: string;
};

type CreateMessageSuccessful = {
	statusCode: StatusCodes.CREATED;
	response: string;
	message: string;
};
type CreateMessageResponse = Omit<Response, 'json'> & {
	json: () => Promise<CreateMessageSuccessful>;
};

const createMessage = async (body: CreateMessageBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/chat', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as CreateMessageResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to create message: ' + (error as Error).message);
	}
};

const chatService = {
	createMessage
};

export default chatService;

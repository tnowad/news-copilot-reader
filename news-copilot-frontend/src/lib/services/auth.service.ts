import type { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';

type SignInBody = {
	email: string;
	password: string;
};

type SignInSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		user: {
			id: number;
			email: string;
			role: string;
			avatar: string;
			displayName: string;
		};
		token: {
			accessToken: string;
			refreshToken: string;
		};
	};
	message: string;
};

type SignInFailed = {
	statusCode: StatusCodes.UNAUTHORIZED;
	message: string;
	error: string;
};

type SignInValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field: 'email' | 'password';
		message: string;
	}[];
};

type SignInResponse = Omit<Response, 'json'> & {
	json: () => Promise<SignInSuccessful | SignInFailed | SignInValidationFailed>;
};

const signIn = async (params: SignInBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/auth/sign-in', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(params),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as SignInResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to sign in: ' + (error as Error).message);
	}
};

const authService = {
	signIn
};

export default authService;

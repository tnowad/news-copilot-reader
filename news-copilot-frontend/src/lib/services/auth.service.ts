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

type SignUpBody = {
	email: string;
	displayName: string;
	password: string;
	confirmPassword: string;
	acceptTerms: boolean;
};

type SignUpSuccessful = {
	statusCode: StatusCodes.CREATED;
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

type SignUpFailed = {
	statusCode: StatusCodes.BAD_REQUEST | StatusCodes.CONFLICT;
	message: string;
	error: string;
};

type SignUpValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field: 'email' | 'password' | 'displayName' | 'confirmPassword' | 'acceptTerms';
		message: string;
	}[];
};

type SignUpResponse = Omit<Response, 'json'> & {
	json: () => Promise<SignUpSuccessful | SignUpFailed | SignUpValidationFailed>;
};

const signUp = async (params: SignUpBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/auth/sign-up', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(params),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as SignUpResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to sign up: ' + (error as Error).message);
	}
};

type RefreshTokenBody = {
	refreshToken: string;
};

type RefreshTokenSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		token: {
			accessToken: string;
		};
	};
	message: string;
};

type RefreshTokenFailed = {
	statusCode: StatusCodes.UNAUTHORIZED;
	message: string;
	error: string;
};

type RefreshTokenResponse = Omit<Response, 'json'> & {
	json: () => Promise<RefreshTokenSuccessful | RefreshTokenFailed>;
};

const refreshToken = async (params: RefreshTokenBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/auth/refresh-token', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(params),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as RefreshTokenResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to refresh token: ' + (error as Error).message);
	}
};

const authService = {
	signIn,
	signUp,
	refreshToken
};

export default authService;

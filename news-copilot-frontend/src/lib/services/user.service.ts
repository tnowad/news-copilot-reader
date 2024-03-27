import { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
import type { Role } from '$lib/types/models';

type GetCurrentUserProfileParams = {
	include?: 'roles'[];
	style?: 'compact' | 'full';
};

type GetCurrentUserProfileSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		user: {
			id: number;
			email: string;
			displayName: string;
			avatarImage: string;

			bio?: string;
			birthDate?: string;
			phoneNumber?: string;

			roles?: Role[];
		};
	};
	message: string;
};

type GetCurrentUserProfileFailed = {
	statusCode: StatusCodes.UNAUTHORIZED;
	message: string;
	error: string;
};

type GetCurrentUserProfileResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetCurrentUserProfileSuccessful | GetCurrentUserProfileFailed>;
};

const getCurrentUserProfile = async (
	params: GetCurrentUserProfileParams = {},
	headers: HeadersInit = {}
): Promise<GetCurrentUserProfileSuccessful | GetCurrentUserProfileFailed> => {
	try {
		const { include, style } = params;
		const queryParams = new URLSearchParams();

		if (include) {
			include.forEach((param) => queryParams.append('include', param));
		}

		if (style) {
			queryParams.set('style', style);
		}

		const url = new URL('/users/profile', API_URL);
		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetCurrentUserProfileResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to get current user profile: ' + (error as Error).message);
	}
};

type UpdateCurrentUserProfileBody = {
	email: string;
	displayName: string;
	avatarImage: string;

	bio?: string;
	birthDate?: string;
	phoneNumber?: string;

}

type UpdateCurrentUserProfileSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		user: {
			id: number;
			email: string;
			displayName: string;
			avatarImage: string;

			bio?: string;
			birthDate?: string;
			phoneNumber?: string;

		};
	};
	message: string;
};

type UpdateCurrentUserProfileValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field: 'id' | 'displayName' | 'avatarImage' | 'email' | 'phoneNumber';
		message: string;
	}[];
};

type UpdateCurrentUserProfilePermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

type UpdateCurrentUserProfileNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type UpdateCurrentUserProfileServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type UpdateCurrentUserProfileReponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| UpdateCurrentUserProfileSuccessful
		| UpdateCurrentUserProfilePermissionDenied
		| UpdateCurrentUserProfileValidationFailed
		| UpdateCurrentUserProfileNotFound
		| UpdateCurrentUserProfileServerError
	>;
};

const updateCurrentUser = async (body: UpdateCurrentUserProfileBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL(`/users/profile`, API_URL);
		const requestInit: RequestInit = {
			method: 'PUT',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as UpdateCurrentUserProfileReponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to update user: ' + (error as Error).message);
	}
};

const userService = {
	getCurrentUserProfile,
	updateCurrentUser,
};

export default userService;

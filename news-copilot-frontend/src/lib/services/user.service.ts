import { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
import type { Role } from '$lib/types/models';

type GetCurrentUserProfileParams = {
	include?: ('roles' | 'avatar')[];
	style?: 'compact' | 'full';
};

type GetCurrentUserProfileSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		user: {
			id: number;
			email: string;
			displayName: string;
			avatarImage?: string;
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

		const url = new URL('/user/profile', API_URL);
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

const userService = {
	getCurrentUserProfile
};

export default userService;

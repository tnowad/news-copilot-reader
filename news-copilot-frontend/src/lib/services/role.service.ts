import type { StatusCodes } from 'http-status-codes';
import type { Role } from './types';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';

type GetAllRolesParams = {
	style?: 'compact' | 'full';
	includes?: 'users'[];
};

type GetAllRolesSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		roles: Role[];
	};
	message: string;
};

type GetAllRolesServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type GetAllRolesResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetAllRolesSuccessful | GetAllRolesServerError>;
};

const getAllRoles = async (params: GetAllRolesParams = {}, headers: HeadersInit = {}) => {
	try {
		const { style, includes } = params;
		const url = new URL('/roles', API_URL);
		const queryParams = new URLSearchParams();

		if (style) queryParams.set('style', style);
		if (includes) includes.forEach((param) => queryParams.append('includes', param));

		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetAllRolesResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch articles: ' + (error as Error).message);
	}
};

const roleService = { getAllRoles };

export default roleService;

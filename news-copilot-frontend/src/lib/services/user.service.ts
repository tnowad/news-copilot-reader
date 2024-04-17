import { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
import type { Metadata } from './types';

type GetCurrentUserProfileParams = {
	include?: 'roles'[];
	style?: 'compact' | 'full';
};

type GetCurrentUserProfileSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		user: User;
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
	email?: string;
	displayName?: string;
	avatarImage?: string;
	password: string;
	newPassword?: string;

	bio?: string;
	birthDate?: string;
	phoneNumber?: string;
};

type UpdateCurrentUserProfileSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		user: User;
	};
	message: string;
};

type UpdateCurrentUserProfileValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field:
			| 'id'
			| 'displayName'
			| 'avatarImage'
			| 'email'
			| 'phoneNumber'
			| 'bio'
			| 'birthDate'
			| 'password'
			| 'newPassword'
			| 'confirmPassword';
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

// TODO: GET ALL USERS
type GetAllUsersParams = {
	page?: number;
	limit?: number;
	search?: string;
	sortBy?: 'id' | 'email' | 'displayName' | 'phoneNumber';
	sortOrder?: 'asc' | 'desc';
	style?: 'compact' | 'full';
	includes?: 'roles'[];
};

type GetAllUsersSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		users: User[];
		metadata: Metadata;
	};
	message: string;
};
type GetALlUsersFailed = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};
type GetAllUsersResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetAllUsersSuccessful | GetALlUsersFailed>;
};
const getAllUsers = async (
	params: GetAllUsersParams = {},
	headers: HeadersInit = {}
): Promise<GetAllUsersSuccessful | GetALlUsersFailed> => {
	try {
		const { page, limit, search, sortBy, sortOrder, style, includes } = params;
		const url = new URL('/users', API_URL);
		const queryParams = new URLSearchParams();

		if (page) queryParams.set('page', page.toString());
		if (limit) queryParams.set('limit', limit.toString());
		if (search) queryParams.set('search', search);
		if (sortBy) queryParams.set('sortBy', sortBy);
		if (sortOrder) queryParams.set('sortOrder', sortOrder);
		if (style) queryParams.set('style', style);
		if (includes) includes.forEach((param) => queryParams.append('includes', param));

		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetAllUsersResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch articles: ' + (error as Error).message);
	}
};

type deleteUserSuccessful = {
	statusCode: StatusCodes.OK;
	message: string;
};
type deleteUserFailed = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};
type deleteUserResponse = Omit<Response, 'json'> & {
	json: () => Promise<deleteUserSuccessful | deleteUserFailed>;
};
const deleteUser = async (
	id: number,
	headers: HeadersInit = {}
): Promise<deleteUserSuccessful | deleteUserFailed> => {
	try {
		const url = new URL(`/users/${id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'DELETE',
			headers: { ...defaultHeaders, ...headers }
		};
		const response = (await fetch(url, requestInit)) as deleteUserResponse;
		return response.json();
	} catch (error) {
		throw new Error('Failed to delete user: ' + (error as Error).message);
	}
};

// TODO: CREATE USER
type User = {
	id: number;
	email: string;
	displayName: string;
	avatarImage: string;
	bio?: string;
	birthDate?: string;
	phoneNumber?: string;
	roles?: string[];
};

type CreateUserBody = {
	email: string;
	password: string;
	displayName: string;
	avatarImage?: string;
	bio?: string;
	birthDate?: string;
	phoneNumber?: string;
};

type CreateUserSuccessful = {
	statusCode: StatusCodes.CREATED;
	message: string;
	data: {
		user: User;
	};
};

type CreateUserBadRequest = {
	statusCode: StatusCodes.BAD_REQUEST;
	message: string;
	error: string;
};

type CreateUserResponse = Omit<Response, 'json'> & {
	json: () => Promise<CreateUserSuccessful | CreateUserBadRequest>;
};

const createUser = async (body: CreateUserBody, headers: HeadersInit = {}) => {
	try {
		const url = new URL('/users', API_URL);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as CreateUserResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to create user: ' + (error as Error).message);
	}
};

type GetUserParams = {
	id?: number;
	include?: 'roles'[];
	style?: 'compact' | 'full';
};

type GetUserSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		user: User;
	};
	message: string;
};

type GetUserFailed = {
	statusCode: StatusCodes.UNAUTHORIZED;
	message: string;
	error: string;
};

type GetUserResponse = Omit<Response, 'json'> & {
	json: () => Promise<GetUserSuccessful | GetUserFailed>;
};

const getUser = async (
	params: GetUserParams = {},
	headers: HeadersInit = {}
): Promise<GetUserSuccessful | GetCurrentUserProfileFailed> => {
	try {
		const { id, include, style } = params;
		const queryParams = new URLSearchParams();

		if (include) {
			include.forEach((param) => queryParams.append('include', param));
		}

		if (style) {
			queryParams.set('style', style);
		}

		const url = new URL(`/users/${id}`, API_URL);
		url.search = queryParams.toString();

		const requestInit: RequestInit = {
			method: 'GET',
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as GetUserResponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to get current user profile: ' + (error as Error).message);
	}
};

type UpdateUserBody = {
	id?: number;
	email?: string;
	displayName?: string;
	avatarImage?: string;
	password: string;
	newPassword?: string;
	roleIds?: number[];

	bio?: string;
	birthDate?: string;
	phoneNumber?: string;
};

type UpdateUserSuccessful = {
	statusCode: StatusCodes.OK;
	data: {
		user: User;
	};
	message: string;
};

type UpdateUserValidationFailed = {
	statusCode: StatusCodes.UNPROCESSABLE_ENTITY;
	message: string;
	errors: {
		field:
			| 'id'
			| 'displayName'
			| 'avatarImage'
			| 'email'
			| 'phoneNumber'
			| 'bio'
			| 'birthDate'
			| 'password'
			| 'newPassword'
			| 'confirmPassword';
		message: string;
	}[];
};

type UpdateUserPermissionDenied = {
	statusCode: StatusCodes.FORBIDDEN;
	message: string;
	error: string;
};

type UpdateUserNotFound = {
	statusCode: StatusCodes.NOT_FOUND;
	message: string;
	error: string;
};

type UpdateUserServerError = {
	statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
	message: string;
	error: string;
};

type UpdateUserReponse = Omit<Response, 'json'> & {
	json: () => Promise<
		| UpdateUserSuccessful
		| UpdateUserPermissionDenied
		| UpdateUserValidationFailed
		| UpdateUserNotFound
		| UpdateUserServerError
	>;
};

const updateUser = async (body: UpdateUserBody, headers: HeadersInit = {}) => {
	try {
		const { id } = body;
		const url = new URL(`/users/${id}`, API_URL);
		const requestInit: RequestInit = {
			method: 'PUT',
			body: JSON.stringify(body),
			headers: { ...defaultHeaders, ...headers }
		};

		const response = (await fetch(url, requestInit)) as UpdateUserReponse;

		return response.json();
	} catch (error) {
		throw new Error('Failed to update user: ' + (error as Error).message);
	}
};

const userService = {
	getCurrentUserProfile,
	updateCurrentUser,
	getAllUsers,
	getUser,
	deleteUser,
	createUser,
	updateUser
};

export default userService;

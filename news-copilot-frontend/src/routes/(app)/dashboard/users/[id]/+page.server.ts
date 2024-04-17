import roleService from '$lib/services/role.service';
import uploadService from '$lib/services/upload.service';
import userService from '$lib/services/user.service';
import { redirect } from '@sveltejs/kit';
import { StatusCodes } from 'http-status-codes';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const accessToken = event.cookies.get('accessToken');
	const id = +event.params.id;

	if (!accessToken) {
		redirect(StatusCodes.TEMPORARY_REDIRECT, '/sign-in');
	}

	const userResponse = await userService.getUser(
		{ include: ['roles'], style: 'full', id },
		{ Authorization: `Bearer ${accessToken}` }
	);

	const rolesResponse = await roleService.getAllRoles();

	const user = userResponse.statusCode === StatusCodes.OK ? userResponse.data.user : null;
	const roles = rolesResponse.statusCode === StatusCodes.OK ? rolesResponse.data.roles : [];

	return { user: user, roles };
};

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const id = +event.params.id;
		const email = formData.get('email') as string;
		const birthDate = formData.get('birthDate') as string;
		const phoneNumber = formData.get('phoneNumber') as string;
		const password = formData.get('password') as string;
		const newPassword = formData.get('newPassword') as string;
		const displayName = formData.get('displayName') as string;
		const avatarImage = formData.get('avatarImage') as File;
		const bio = formData.get('bio') as string;
		const roleIds = (formData.getAll('roleIds') as string[]).map(Number);
		let avatarURL;

		if (avatarImage) {
			avatarURL = await uploadService.uploadFile(avatarImage);
		}

		const response = await userService.updateUser(
			{
				id,
				email,
				avatarImage: avatarURL,
				displayName,
				bio,
				phoneNumber,
				birthDate,
				newPassword,
				password,
				roleIds
			},
			{ Authorization: `Bearer ${event.cookies.get('accessToken')}` }
		);

		switch (response.statusCode) {
			case StatusCodes.OK:
				break;
			case StatusCodes.NOT_FOUND:
			case StatusCodes.FORBIDDEN:
				break;
			case StatusCodes.UNPROCESSABLE_ENTITY:
				break;
			default:
		}

		return response;
	}
} satisfies Actions;

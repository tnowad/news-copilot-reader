import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async () => {
	const userMockData = {
		id: 1,
		email: 'tnowad@gmail.com',
		displayName: 'Tomasz Nowak',
		roles: ['GUEST', 'USER', 'WRITER', 'ADMIN'],
		avatar: 'https://avatars.githubusercontent.com/u/114892052'
	};

	const user = parseInt((Math.random() * 10).toFixed(0)) % 2 == 0 ? userMockData : null;

	return {
		user
	};
};

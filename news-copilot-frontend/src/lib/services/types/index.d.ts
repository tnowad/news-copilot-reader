export type Role = 'USER' | 'WRITER' | 'ADMIN';

export type User = {
	id: number;
	email: string;
	displayName: string;
	avatarImage: string;
	roles?: Role[];
};

export type Role = 'USER' | 'WRITER' | 'ADMIN';

export type User = {
	id: number;
	email: string;
	displayName: string;
	avatarImage: string;
	roles?: Role[];
};

export type Article = {
	id: number;
	title: string;
	slug: string;
	summary: string;
	coverImage: string;
	author?: User;
	content?: string;
	createdAt?: string;
	updatedAt?: string;
	publishedAt?: string;
};

export type Category = {
	id: number;
	title: string;
	slug: string;
	description?: string;
	articles?: Article[];
};

export type RoleEnum = 'USER' | 'WRITER' | 'ADMIN';

export type Token = {
	accessToken: string;
	refreshToken: string;
};

export type User = {
	id: number;
	email: string;
	displayName: string;
	avatarImage: string;
	roles?: RoleEnum[];
};

export type Article = {
	id: number;
	title: string;
	slug: string;
	summary: string;
	coverImage: string;
	categories?: Category[];
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
	createdAt?: string;
	updatedAt?: string;
	deletedAt?: string;

	articles?: Article[];
};

export type Comment = {
	id: number;
	content: string;
	createdAt: string;
	updatedAt: string;
	article?: Article;
	author?: User;
};

export type Bookmark = {
	id: number;
	user: User;
	article: Article;
	createdAt: string;
};

export type Pagination = {
	offset: number;
	limit: number;
	previousOffset: number;
	nextOffset: number;
	currentPage: number;
	pageCount: number;
	totalCount: number;
};

export type Role = {
	id: number;
	name: RoleEnum;
};

export type Style = 'compact' | 'full';

export type Metadata = {
	pagination?: Pagination;
	style?: Style;
};

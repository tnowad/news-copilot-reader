// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces

enum Role {
	USER = 'USER',
	WRITER = 'WRITER',
	ADMIN = 'ADMIN'
}

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			userId: string | null;
			roles: Role[];
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};

import chatService from '$lib/services/chat.service.js';
import type { Actions } from '@sveltejs/kit';

export const load = async (event) => {};

export const actions = {
	default: async (event) => {
		const formData = await event.request.formData();
		const content = formData.get('content') as string;
		const createMessageResponse = await chatService.createMessage({
			message: content
		});
		return {
			content: createMessageResponse.response
		};
	}
};

<script lang="ts">
	import { Section } from 'flowbite-svelte-blocks';
	import { Label, Input, Card } from 'flowbite-svelte';
	import { enhance } from '$app/forms';

	export let data;

	let inputValue = '';

	let messages = [
		{
			id: -1,
			content: 'Hi, how can I help you?',
			type: 'bot'
		}
	];
</script>

<section class="w-full">
	<div class="flex flex-col" style="height: calc(100vh - 100px); overflow-y: auto;">
		{#each messages as message (message.id)}
			<Card
				class="{message.type == 'bot'
					? 'bg-blue-200'
					: 'ml-auto items-end bg-gray-200'} mb-2 rounded p-2"
				size="none"
			>
				<p>{message.content}</p>
			</Card>
		{/each}
	</div>
	<form
		method="post"
		action="/chat"
		use:enhance={({ formData }) => {
			if (!formData.get('content')) {
				return;
			}

			inputValue = '';
			messages = [
				...messages,
				{
					id: messages.length + 1,
					content: formData.get('content'),
					type: 'user'
				}
			];

			return ({ result }) => {
				messages = [
					...messages,
					{
						id: messages.length + 1,
						content: result.data.content,
						type: 'bot'
					}
				];
			};
		}}
	>
		<div class="relative mt-4">
			<Input name="content" class="w-full" placeholder="Message chatbot" bind:value={inputValue} />
		</div>
	</form>
</section>

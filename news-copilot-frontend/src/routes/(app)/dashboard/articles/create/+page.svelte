<script lang="ts">
	import { Label, Input, Button, Select } from 'flowbite-svelte';

	import Markdown from '$lib/widgets/markdown.svelte';
	import Editor from '$lib/widgets/editor.svelte';
	import type { PageServerData } from './$types';
	let source = '';
	const handleSubmit = () => {
		alert('Form submited.');
	};

	export let data: PageServerData;
</script>

<section class="mx-5">
	<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Add a new Article</h2>
	<form on:submit={handleSubmit}>
		<div class="grid gap-4 sm:grid-cols-2 sm:gap-6">
			<div class="sm:col-span-2">
				<Label for="name" class="mb-2">Title</Label>
				<Input type="text" id="name" placeholder="Article Title" required />
			</div>
			<div class="sm:col-span-2">
				<Label for="description" class="mb-2">Description</Label>
				<Editor bind:source />
			</div>
			<Button type="submit" class="w-32">Add product</Button>
		</div>
	</form>

	<div>
		<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Content Preview</h2>

		<div>
			<Markdown bind:source />
		</div>
	</div>
</section>
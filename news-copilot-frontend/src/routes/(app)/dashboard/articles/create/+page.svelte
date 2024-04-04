<script lang="ts">
	import { Label, Input, Button, MultiSelect, Textarea } from 'flowbite-svelte';
	import Markdown from '$lib/widgets/markdown.svelte';
	import Editor from '$lib/widgets/editor.svelte';
	import type { PageData } from './$types';
	let content = '';
	let coverImage = '';
	let summary = '';
	const handleSubmit = () => {};

	let selected: { value: string; name: string }[] = [];
	export let data: PageData;
</script>

<section class="mx-5">
	<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Add a new Article</h2>
	<form action="/dashboard/articles/create" method = 'post'>
		<div class="grid gap-4 sm:grid-cols-2 sm:gap-6">
			<div class="sm:col-span-2">
				<Label for="name" class="mb-2">Title</Label>
				<Input type="text" name = "title" placeholder="Article Title" required />
			</div>
			<div class="sm:col-span-2">
				<Label for="cover-image" class="mb-2">Cover Image</Label>
				<Input
					type="text"
					name = "coverImage"
					placeholder="URL of the cover image"
					bind:value={coverImage}
				/>
			</div>
			<div class="sm:col-span-2">
				<Label for="author-id" class="mb-2">Author ID</Label>
				<Input type="number"  name = "userId" disabled id="author-id" placeholder="Author ID" value={data.user.id} />
			</div>
			<div class="col-span-full">
				<Label for="categories" class="mb-2">Categories</Label>
				<MultiSelect
					name ="category"
					items={data.categories.map((category) => ({
						value: category.id,
						name: category.slug
					}))}
					bind:selected
				/>
			</div>
			<div class="sm:col-span-2">
				<Label for="summary" class="mb-2">Summary</Label>
				<Textarea type="text" name = "summary" id="summary" placeholder="Summary" bind:value={summary} />
			</div>
			<div class="sm:col-span-2">
				<Label for="description" class="mb-2">Content</Label>
				<Editor bind:source={content} />
				<input type="hidden" name="content" bind:value={content} />
			</div>
			<Button type="submit" class="w-32">Add product</Button>
			
		</div>
	</form>

	<div>
		<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Content Preview</h2>
		<div>
			<Markdown bind:source={content} />
		</div>
	</div>
</section>

<script lang="ts">
	import {
		Label,
		Input,
		Button,
		MultiSelect,
		Textarea,
		Breadcrumb,
		BreadcrumbItem
	} from 'flowbite-svelte';
	import Markdown from '$lib/widgets/markdown.svelte';
	import Editor from '$lib/widgets/editor.svelte';
	import type { ActionData } from './$types';
	import { toasts } from 'svelte-toasts';
	import { enhance } from '$app/forms';
	import { StatusCodes } from 'http-status-codes';

	export let data;

	let content = '';
	let categories = data.categories.map((category) => ({
		value: category.id,
		name: category.slug
	}));

	export let form: ActionData;

	$: {
		if (form) {
			switch (form.statusCode) {
				case StatusCodes.CREATED:
					toasts.success(form.message);
					break;
				case StatusCodes.UNPROCESSABLE_ENTITY | StatusCodes.INTERNAL_SERVER_ERROR:
					toasts.error(form.message);
					break;
			}
			console.log(form);
		}
	}
</script>

<section>
	<div>
		<Breadcrumb class="mb-6">
			<BreadcrumbItem home>Home</BreadcrumbItem>
			<BreadcrumbItem
				class="inline-flex items-center text-gray-700 hover:text-primary-600 dark:text-gray-300 dark:hover:text-white"
				href="/dashboard/articles">Articles</BreadcrumbItem
			>
			<BreadcrumbItem>Create</BreadcrumbItem>
		</Breadcrumb>
	</div>
</section>

<section class="mx-5">
	<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Update Article</h2>
	<form action={`/dashboard/articles/create`} method="post" use:enhance>
		<div class="grid gap-4 sm:grid-cols-2 sm:gap-6">
			<div class="sm:col-span-2">
				<Label for="name" class="mb-2">Title</Label>
				<Input type="text" name="title" placeholder="Article Title" required />
			</div>
			<div class="sm:col-span-2">
				<Label for="cover-image" class="mb-2">Cover Image</Label>
				<Input type="text" name="coverImage" placeholder="URL of the cover image" />
			</div>
			<div class="sm:col-span-2">
				<Label for="author-id" class="mb-2">Author ID</Label>
				<Input
					type="number"
					name="userId"
					disabled
					id="author-id"
					placeholder="Author ID"
					value={data.user.id}
				/>
			</div>
			<div class="col-span-full">
				<Label for="categories" class="mb-2">Categories</Label>
				<MultiSelect name="category" items={categories} />
			</div>
			<div class="sm:col-span-2">
				<Label for="summary" class="mb-2">Summary</Label>
				<Textarea type="text" name="summary" id="summary" placeholder="Summary" />
			</div>
			<div class="sm:col-span-2">
				<Label for="description" class="mb-2">Content</Label>
				<Editor bind:content />
				<input type="hidden" name="content" bind:value={content} />
			</div>
			<Button type="submit" class="w-32">Add Article</Button>
		</div>
	</form>

	<div>
		<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Content Preview</h2>
		<div>
			<Markdown bind:source={content} />
		</div>
	</div>
</section>

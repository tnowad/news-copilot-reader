<script lang="ts">
<<<<<<< HEAD
	import { Label, Input, Button, Select } from 'flowbite-svelte';

=======
	import { Label, Input, Button, MultiSelect } from 'flowbite-svelte';
>>>>>>> 7433457cc53c661ca53b6909af53b806e13f8c1b
	import Markdown from '$lib/widgets/markdown.svelte';
	import Editor from '$lib/widgets/editor.svelte';
	import type { PageData } from './$types';

	let source = '';
<<<<<<< HEAD
	const handleSubmit = () => {
		alert('Form submited.');
		console.log(selectedCategory);
	};
	let selectedCategory: any;
	
	export let data: PageData;
	const categoriesItems = data.categories.map((category) => ({
		name: category.title, 
		value: category.id 
	}));
=======

	export let data: PageData;

	const handleSubmit = () => {
		alert('Form submitted.');
	};

	let selected: { value: string; name: string }[] = [];
>>>>>>> 7433457cc53c661ca53b6909af53b806e13f8c1b
</script>

<section class="mx-5">
	<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Add a new Article</h2>
	<form on:submit={handleSubmit}>
		<div class="grid gap-4 sm:grid-cols-2 sm:gap-6">
			<div class="sm:col-span-2">
				<Label for="name" class="mb-2">Title</Label>
				<Input type="text" id="name" placeholder="Article Title" required />
			</div>
			<div class="col-span-full">
				<Label for="categories" class="mb-2">Categories</Label>
				<MultiSelect
					items={data.categories.map((category) => ({
						value: category.id,
						name: category.slug
					}))}
					bind:selected
				/>
			</div>
			<div class="sm:col-span-2">
				<Label for="name" class="mb-2">Categories</Label>
				<Select
					id="select"
					items={categoriesItems}
					bind:value = {selectedCategory}
				/>
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

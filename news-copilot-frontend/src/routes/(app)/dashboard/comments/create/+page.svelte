<script lang="ts">
	import { Card } from 'flowbite-svelte';
	import Markdown from '$lib/widgets/markdown.svelte';

	let content = '';

	const handleSubmit = () => {};
</script>

<section class="mx-5">
	<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Comment Article</h2>
	<form on:submit={handleSubmit}>
		<div class="grid gap-4 sm:grid-cols-2 sm:gap-6">
			<Card href="/articles" class="mx-auto">
				<h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
					Noteworthy technology acquisitions 2021
				</h5>
				<p class="font-normal leading-tight text-gray-700 dark:text-gray-400">
					Here are the biggest enterprise technology acquisitions of 2021 so far, in reverse
					chronological order.
				</p>
			</Card>
		</div>
	</form>

	<div>
		<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">Content Preview</h2>
		<div>
			<Markdown bind:source={content} />
		</div>
	</div>
</section>

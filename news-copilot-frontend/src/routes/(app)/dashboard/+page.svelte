<script lang="ts">
	import { Chart, Card } from 'flowbite-svelte';
	import { Section, Social } from 'flowbite-svelte-blocks';
	export let data;
	$: console.log(data);
</script>

<section class="h-full w-full">
	<div class="container grid h-full w-full grid-cols-12">
		<Card class="col-span-6" size="none">
			<Chart class="w-full" options={data.categoryArticleCount} />
		</Card>
	</div>
</section>
<br />
<Card class="col-span-6" size="none">
	<Social>
		<div class="flex flex-col items-center justify-center">
			<dt class="mb-2 text-3xl font-extrabold md:text-4xl">
				{data.articlesStatistics?.totalArticles}
			</dt>
			<dd class="font-light text-gray-500 dark:text-gray-400">Articles</dd>
		</div>
		<div class="flex flex-col items-center justify-center">
			<dt class="mb-2 text-3xl font-extrabold md:text-4xl">
				{data.articlesStatistics?.totalUser}
			</dt>
			<dd class="font-light text-gray-500 dark:text-gray-400">Users</dd>
		</div>
		<div class="flex flex-col items-center justify-center">
			<dt class="mb-2 text-3xl font-extrabold md:text-4xl">
				{data.articlesStatistics?.totalCategories}
			</dt>
			<dd class="font-light text-gray-500 dark:text-gray-400">Categories</dd>
		</div>
	</Social>
</Card>

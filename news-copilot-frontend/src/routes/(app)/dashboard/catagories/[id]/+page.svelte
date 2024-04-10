<script lang="ts">
	import ArticleSection from '$lib/widgets/article-section.svelte';
	import { Card, Button, Pagination } from 'flowbite-svelte';
	import { ArrowRightOutline } from 'flowbite-svelte-icons';
	import { PageData } from '../../../(default)/categories/[slug]/[id]/$types';
	export let data: PageData;
</script>

<div>
	{#if data.category}
		<Card>
			<h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
				{data.category.title}
			</h5>
			{#if data.category.description}
				<p class="mb-3 font-normal leading-tight text-gray-700 dark:text-gray-400">
					{data.category.description}
				</p>
			{/if}
			<Button class="w-fit">
				Read more <ArrowRightOutline class="ms-2 h-3.5 w-3.5 text-white" />
			</Button>
		</Card>
	{:else}
		<p>Không có dữ liệu.</p>
	{/if}
	<ArticleSection articles={data.articles} />
	<Pagination />
</div>

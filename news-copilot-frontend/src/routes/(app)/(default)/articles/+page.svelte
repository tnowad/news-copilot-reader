<script lang="ts">
	import type { PageData } from './$types';
	export let data: PageData;
	import ArticleSection from '$lib/widgets/article-section.svelte';
	import { Button, Modal, Checkbox, ButtonGroup, Input } from 'flowbite-svelte';
	import { ChevronLeftOutline, ChevronRightOutline } from 'flowbite-svelte-icons';
	let isShowAdvanceSearch = false;

	let page = +(data.metadata?.pagination.currentPage ?? 1);
	let limit = +(data.metadata?.pagination.limit ?? 10);
	let searchQuery = data.metadata?.filters?.search ?? '';

	const gotoPage = (
		nextPage: number = page,
		nextLimit: number = limit,
		nextSearch: string = searchQuery
	) => {
		if (!browser) {
			return;
		}
		const url = new URL(window.location.href);
		url.searchParams.set('page', nextPage + '');
		url.searchParams.set('limit', nextLimit + '');
		url.searchParams.set('search', nextSearch);

		goto(url.toString(), {
			noScroll: true,
			keepFocus: true
		});
	};
</script>

<div>
	<form action="/articles" method="get">
		<ArticleSection title="Displaying search results" articles={data.articles}>
			<svelte:fragment slot="filters">
				<div class="flex space-x-4">
					<Button
						on:click={() => {
							isShowAdvanceSearch = true;
						}}>Filter</Button
					>
				</div>

				<Modal bind:open={isShowAdvanceSearch} size="xs" autoclose={false} class="w-full">
					<h3 class="text-xl font-medium text-gray-900 dark:text-white">Filter by category</h3>
					<div class="grid grid-cols-2 gap-2 md:grid-cols-3">
						{#if data.categories}
							{#each data.categories as category}
								<div class="flex items-center">
									<Checkbox name="categoryIds" value={category.id}>{category.title}</Checkbox>
								</div>
							{/each}
						{/if}
					</div>
					<div class="flex items-center space-x-4 rounded-b dark:border-gray-600">
						<Button type="submit">Apply</Button>
						<Button href="/articles">Reset</Button>
					</div>
				</Modal>
			</svelte:fragment>
			<svelte:fragment slot="pagination">
				{#if data.metadata}
					<span class="text-sm font-normal text-gray-500 dark:text-gray-400">
						Showing
						<span class="font-semibold text-gray-900 dark:text-white"
							>{data.metadata.pagination.offset}-{data.metadata.pagination.nextOffset}</span
						>
						of
						<span class="font-semibold text-gray-900 dark:text-white"
							>{data.metadata.pagination.totalCount}</span
						>
					</span>
					<ButtonGroup>
						<Button
							on:click={() => {
								if (data.metadata && !(+data.metadata.pagination.currentPage <= 1)) {
									page = page - 1;
									gotoPage(page - 1, limit);
								}
							}}><ChevronLeftOutline size="xs" class="m-1.5" /></Button
						>
						<Input
							type="number"
							name="page"
							defaultValue={page}
							bind:value={page}
							min="1"
							max={data.metadata.pagination.pageCount}
							class="w-16 text-center"
						/>
						<Button
							on:click={() => {
								if (
									data.metadata &&
									!(
										+data.metadata.pagination.currentPage >=
										+data.metadata.pagination.pageCount - 1
									)
								) {
									page = page + 1;
									gotoPage(page + 1);
								}
							}}><ChevronRightOutline size="xs" class="m-1.5" /></Button
						>
					</ButtonGroup>
				{/if}
			</svelte:fragment>
		</ArticleSection>
	</form>
</div>

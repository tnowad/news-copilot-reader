<script lang="ts">
	import type { PageData } from './$types';
	import { Card, Button } from 'flowbite-svelte';
	import { ArrowRightOutline } from 'flowbite-svelte-icons';
	export let data: PageData;
	console.log({ data: data });
</script>

<div>
	{#if data && Array.isArray(data.category)}
		{#each data.category as item (item.id)}
			<Card>
				<h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
					{item.title}
				</h5>
				{#if item.description}
					<p class="mb-3 font-normal leading-tight text-gray-700 dark:text-gray-400">
						{item.description}
					</p>
				{/if}
				<Button class="w-fit">
					Read more <ArrowRightOutline class="ms-2 h-3.5 w-3.5 text-white" />
				</Button>
			</Card>
		{/each}
	{:else}
		<p>Không có dữ liệu.</p>
	{/if}
</div>

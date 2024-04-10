<script lang="ts">
	import { goto } from '$app/navigation';
	import { Input, Button, Modal, Search, Listgroup, ListgroupItem, Card } from 'flowbite-svelte';
	import { ArrowRightOutline, SearchOutline } from 'flowbite-svelte-icons';

	let query = '';

	let isOpenSearchModal = false;
	const toggleSearchModal = () => {
		isOpenSearchModal = !isOpenSearchModal;
	};

	let searchResults: {
		id: number;
		title: string;
		summary: string;
		coverImage: string;
		slug: string;
	}[] = [];

	const mockArticles = [
		{
			id: 1,
			title: 'How to build a website using SvelteKit',
			summary: 'Learn how to build a website using SvelteKit and deploy it to Vercel.',
			coverImage: '/images/default-news-cover.png',
			slug: 'how-to-build-a-website-using-sveltekit'
		},
		{
			id: 2,
			title: 'How to build a website using SvelteKit',
			summary: 'Learn how to build a website using SvelteKit and deploy it to Vercel.',
			coverImage: '/images/default-news-cover.png',
			slug: 'how-to-build-a-website-using-sveltekit'
		},
		{
			id: 3,
			title: 'How to build a website using SvelteKit',
			summary: 'Learn how to build a website using SvelteKit and deploy it to Vercel.',
			coverImage: '/images/default-news-cover.png',
			slug: 'how-to-build-a-website-using-sveltekit'
		},
		{
			id: 4,
			title: 'How to build a website using SvelteKit',
			summary: 'Learn how to build a website using SvelteKit and deploy it to Vercel.',
			coverImage: '/images/default-news-cover.png',
			slug: 'how-to-build-a-website-using-sveltekit'
		}
	];

	const getAllArticles = async (query: string) => {
		const response = await fetch(`/api/articles?search=${query}`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
		});
		const data = await response.json();
		return data.data.articles;
	};

	let debounceId: number | null;

	const handleSearch = (event: Event) => {
		const target = event.target as HTMLInputElement;
		if (target.value === '') {
			return;
		}

		if (debounceId) {
			clearTimeout(debounceId);
		}
		debounceId = setTimeout(async () => {
			searchResults = await getAllArticles(target.value);
		}, 300) as unknown as number;
	};
</script>

<Button
	color="none"
	data-collapse-toggle="mobile-menu-3"
	aria-controls="mobile-menu-3"
	aria-expanded="false"
	class="me-1 rounded-lg p-2.5 text-sm text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-4 focus:ring-gray-200 lg:hidden dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-700"
	on:click={toggleSearchModal}
>
	<SearchOutline class="h-5 w-5" />
</Button>

<div class="relative hidden lg:block">
	<div class="pointer-events-none absolute inset-y-0 start-0 flex items-center ps-3">
		<SearchOutline class="h-4 w-4" />
	</div>
	<Input id="search-navbar" class="ps-10" placeholder="Search..." on:focus={toggleSearchModal} />
</div>

<Modal class="mt-0" bind:open={isOpenSearchModal} placement="top-center" size="xl">
	<slot name="header">
		<Search on:keydown={handleSearch} class="mt-8" bind:value={query} />
	</slot>
	{#each searchResults as article}
		<a
			href={`/articles/${article.slug}/${article.id}`}
			class="flex max-h-20"
			on:click={toggleSearchModal}
		>
			<div class="h-20 w-20">
				<img src={article.coverImage} alt={article.title} class="h-full w-full object-cover" />
			</div>
			<div>
				<h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
					{article.title}
				</h5>
				<p class="mb-3 font-normal leading-tight text-gray-700 dark:text-gray-400">
					{article.summary}
				</p>
			</div>
		</a>
	{/each}
	<slot name="footer">
		<div class="flex justify-end">
			<Button href={`/search?search=${query}`} on:click={toggleSearchModal}
				>Show more <ArrowRightOutline class="ml-2 h-5 w-5" /></Button
			>
		</div>
	</slot>
</Modal>

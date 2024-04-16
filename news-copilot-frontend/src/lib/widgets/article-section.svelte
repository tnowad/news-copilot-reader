<script lang="ts">
	import {
		Section,
		ArticleAuthor,
		ArticleBody,
		ArticleHead,
		ArticleWrapper,
		BlogBodyWrapper,
		BlogHead
	} from 'flowbite-svelte-blocks';
	import { Avatar, Badge, Img } from 'flowbite-svelte';
	import type { Article } from '$lib/services/types';

	export let articles: Article[] = [];
	export let title: string;
</script>

<Section name="none" sectionClass="container mx-auto">
	{#if title}
		<BlogHead h2Class="text-start font-bold text-2xl mb-2" divClass="max-w-none">
			<svelte:fragment slot="h2">{title}</svelte:fragment>
		</BlogHead>
	{/if}

	<BlogBodyWrapper divClass="grid gap-2 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
		{#if articles?.length === 0}
			<div class="col-span-4">
				<p class="text-center text-xl font-semibold dark:text-white">No articles found</p>
			</div>
		{:else}
			{#each articles ?? [] as article}
				<ArticleWrapper
					articleClass="p-6 bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700 h-full flex flex-col"
				>
					<ArticleHead divClass="">
						<Img
							imgClass="h-48 w-full object-cover rounded-md"
							src={article.coverImage ?? '/images/logo.png'}
						/>
						{#if article.categories}
							<div class="mt-2 flex flex-wrap gap-1">
								{#each article.categories as category}
									<Badge>
										{category.title.toUpperCase()}
									</Badge>
								{/each}
							</div>
						{/if}
					</ArticleHead>

					<a href={`/articles/${article.slug}/${article.id}`}>
						<ArticleBody
							h2Class="flex-grow mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white"
						>
							<svelte:fragment slot="h2">{article.title}</svelte:fragment>
							<svelte:fragment slot="paragraph">
								<p class="mb-5 flex-grow font-light text-gray-500 dark:text-gray-400">
									{article.summary.slice(0, 100) + '...'}
								</p>
							</svelte:fragment>
						</ArticleBody>
					</a>

					<ArticleAuthor>
						<div slot="author" class="flex space-x-5">
							<Avatar
								class="h-10 w-10"
								src={article.author?.avatarImage}
								alt={article.author?.displayName}
							/>
							<div class="flex flex-col">
								<h4 class="text-sm font-bold dark:text-white">
									{article.author?.displayName}
								</h4>
								{#if article.createdAt}
									<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
										{new Date(article.createdAt).toLocaleDateString()}
									</p>
								{/if}
							</div>
						</div>
					</ArticleAuthor>
				</ArticleWrapper>
			{/each}
		{/if}
	</BlogBodyWrapper>
</Section>

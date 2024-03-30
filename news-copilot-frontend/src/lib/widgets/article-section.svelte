<script lang="ts">
	import {
		Section,
		ArticleAuthor,
		ArticleBody,
		ArticleHead,
		ArticleWrapper,
		BlogHead,
		BlogBodyWrapper
	} from 'flowbite-svelte-blocks';
	import { Img } from 'flowbite-svelte';
	import { ArrowRightOutline } from 'flowbite-svelte-icons';
	import type { Article } from '$lib/services/types';

	export let articles: Article[] = [];
</script>

<Section name="blog">
	<BlogBodyWrapper divClass="grid grid-cols-4 gap-2">
		{#if articles?.length === 0}
			<div class="col-span-4">
				<p class="text-center text-xl font-semibold dark:text-white">No articles found</p>
			</div>
		{:else}
			{#each articles ?? [] as article}
				<ArticleWrapper>
					<ArticleHead>
						<Img src={article.coverImage} />
					</ArticleHead>
					<ArticleBody>
						<svelte:fragment slot="h2"><a href="/">{article.title}</a></svelte:fragment>
						<svelte:fragment slot="paragraph">
							<p class="mb-5 font-light text-gray-500 dark:text-gray-400">{article.summary}</p>
						</svelte:fragment>
					</ArticleBody>
					<ArticleAuthor>
						<svelte:fragment slot="author">
							<Img
								class="h-7 w-7 rounded-full"
								src={article.author?.avatarImage}
								alt={article.author?.displayName}
							/>
							<span class="font-medium dark:text-white"> {article.author?.displayName} </span>
						</svelte:fragment>
						<a
							href={`/articles/${article.slug}/${article.id}`}
							class="inline-flex items-center font-medium text-primary-600 hover:underline dark:text-primary-500"
						>
							Read more
							<ArrowRightOutline size="sm" class="ml-2" />
						</a>
					</ArticleAuthor>
				</ArticleWrapper>
			{/each}
		{/if}
	</BlogBodyWrapper>
</Section>

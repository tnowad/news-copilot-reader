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
	import { VideoCameraSolid, ArrowRightOutline, NewspapperSolid } from 'flowbite-svelte-icons';
	import type { PageData } from './$types';
	export let data: PageData;
</script>

<div>
	<Section name="blog">
		<BlogBodyWrapper divClass="grid grid-cols-4 gap-2">
			{#each data.latestArticle as article}
				<ArticleWrapper>
					<ArticleHead>
						<span class="text-sm">
							<Img src={article.coverImage} />
						</span>
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
								src={article.author.avatarImage}
								alt={article.author.displayName}
							/>
							<span class="font-medium dark:text-white"> {article.author.displayName} </span>
						</svelte:fragment>
						<a
							href={article.slug}
							class="text-primary-600 dark:text-primary-500 inline-flex items-center font-medium hover:underline"
						>
							Read more
							<ArrowRightOutline size="sm" class="ml-2" />
						</a>
					</ArticleAuthor>
				</ArticleWrapper>
			{/each}
		</BlogBodyWrapper>
	</Section>
	<!--<div>Slider Breaking news (Most trending news)</div> 
	<div>Recommendation news (Generate for each user)</div>
	<div>News from followed author</div>
	<div>Hot news each categories</div>
	<div>Latest news</div>
	{#each data.latestArticle as article}
		<h1>
			{article.title}
			{article.author.displayName}
			
		</h1>
	{/each}-->
</div>

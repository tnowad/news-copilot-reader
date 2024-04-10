<script lang="ts">
	import type { PageData } from './$types';
	import ArticleSection from '$lib/widgets/article-section.svelte';

	export let data: PageData;
</script>

<div>
	<ArticleSection title="Recommend for you" articles={data.recommendArticles} />
	<ArticleSection title="Hot News" articles={data.hotArticles} />
	<ArticleSection title="Latest News" articles={data.latestArticles} />

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

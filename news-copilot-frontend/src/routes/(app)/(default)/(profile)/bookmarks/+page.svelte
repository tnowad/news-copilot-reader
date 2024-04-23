<script lang="ts">
	import type { PageData } from './$types';
	export let data: PageData;
	import ArticleSection from '$lib/widgets/article-section.svelte';
</script>

<div>
	<ArticleSection title="Bookmarked Articles" articles={data.articles} />
</div>

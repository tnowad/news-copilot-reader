<script lang="ts">
	import type { PageData } from './$types';
	import Markdown from '$lib/widgets/markdown.svelte';

	export let data: PageData;
</script>

<div class="container mx-auto">
	<h1>{data.article?.title}</h1>
	<img src={data.article?.coverImage} alt="" />
	<Markdown source={data.article?.content} />
</div>

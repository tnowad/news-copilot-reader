<script lang="ts">
	import { DatabaseOutline } from 'flowbite-svelte-icons';
	import type { PageData } from './$types';
	import Markdown from '$lib/widgets/markdown.svelte';

	export let data: PageData;
</script>

<div class="container mx-auto">
	<h1>{data.article?.title}</h1>
	<h1>{data.article?.content}</h1>
	<Markdown />
	<img src={data.article?.coverImage} alt="" />
</div>

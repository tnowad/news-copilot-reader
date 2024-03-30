<script lang="ts">
	import { DatabaseOutline } from 'flowbite-svelte-icons';

	export let data;
</script>

<div>
	<!-- temporary display -->
	<h1>{data.article?.title}</h1>
	<h1>{data.article?.content}</h1>
	<img src={data.article?.coverImage} alt="" />
</div>

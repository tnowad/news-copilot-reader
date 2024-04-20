<script lang="ts">
	import { Chart, Card } from 'flowbite-svelte';
	export let data;
	$: console.log(data);
</script>

<section class="h-full w-full">
	<div class="container grid h-full w-full grid-cols-12">
		<Card class="col-span-6" size="none">
			<Chart class="w-full" options={data.categoryArticleCount} />
		</Card>
	</div>
</section>

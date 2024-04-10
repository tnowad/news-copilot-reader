<script lang="ts">
	export let depth: number;
	export let text: string;
</script>

{#if depth == 1}
	<h1 id={text} class="my-6 border-b border-b-slate-500 pb-2 text-3xl dark:text-white">
		{text}
	</h1>
{:else if depth == 2}
	<h2 id={text} class="my-6 text-2xl dark:text-white">{text}</h2>
{:else if depth == 3}
	<h3 id={text} class="my-6 text-xl dark:text-white">{text}</h3>
{:else if depth == 4}
	<h4 id={text} class="text-md my-6 dark:text-white">{text}</h4>
{:else if depth == 5}
	<h5 id={text} class="my-6 text-sm dark:text-white">{text}</h5>
{:else if depth == 6}
	<h6 id={text} class="my-6 text-sm dark:text-white">{text}</h6>
{:else}
	{text}
{/if}

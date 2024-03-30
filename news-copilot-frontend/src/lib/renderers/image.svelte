<script lang="ts">
	export let href: string;
	export let alt: string;
	export let text: string;
</script>

<div class="my-6 flex flex-col items-center justify-center space-y-3 align-middle">
	<img src={href} {alt} class="h-96 rounded-md object-contain" />
	{#if text}
		<p class="px-12 text-center italic">{text}</p>
	{/if}
</div>

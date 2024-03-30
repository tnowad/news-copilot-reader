<script lang="ts">
	import { List, Li } from 'flowbite-svelte';
	export let ordered: boolean;
</script>

{#if ordered}
	<List tag="ol" class="mt-2 space-y-1 ps-5">
		<slot />
	</List>
{:else}
	<List tag="ul" class="mt-2 space-y-1 ps-5">
		<slot />
	</List>
{/if}

<script lang="ts">
	import { A } from 'flowbite-svelte';
	export let href: string;
	export let text: string;
</script>

<A {href}>
	{text}
</A>

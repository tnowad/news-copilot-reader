<!-- SanitizedInput.svelte -->
<script>
	import { onMount } from 'svelte';
	import DOMPurify from 'dompurify';

	export let text = '';

	let sanitizedHTML = '';

	onMount(() => {
		sanitizedHTML = DOMPurify.sanitize(text);
	});
</script>

<!-- eslint-disable -->
{@html sanitizedHTML}

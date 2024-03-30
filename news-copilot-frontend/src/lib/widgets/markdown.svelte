<script lang="ts">
	import Code from '$lib/renderers/code.svelte';
	import Heading from '$lib/renderers/heading.svelte';
	import Image from '$lib/renderers/image.svelte';
	import Link from '$lib/renderers/link.svelte';
	import ListItem from '$lib/renderers/list-item.svelte';
	import List from '$lib/renderers/list.svelte';
	import Paragraph from '$lib/renderers/paragraph.svelte';
	import { Hr, Table, TableBody, TableBodyCell, TableBodyRow } from 'flowbite-svelte';
	import SvelteMarkdown from 'svelte-markdown';
	import Html from '$lib/renderers/html.svelte';
	import Blockquote from '$lib/renderers/blockquote.svelte';

	export let source: string = '';
</script>

<SvelteMarkdown
	{source}
	renderers={{
		image: Image,
		heading: Heading,
		link: Link,
		list: List,
		paragraph: Paragraph,
		listitem: ListItem,
		table: Table,
		tablebody: TableBody,
		tablecell: TableBodyCell,
		tablerow: TableBodyRow,
		hr: Hr,
		code: Code,
		html: Html,
		blockquote: Blockquote
	}}
/>

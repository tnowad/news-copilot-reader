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

	let source = `# Markdown Elements

## Headings

# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

## Text Styling

*Italic Text*
**Bold Text**
***Bold and Italic Text***
~~Strikethrough Text~~
\`Inline Code\`

## Lists

### Unordered List
- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2
- Item 3

### Ordered List
1. Item 1
2. Item 2
3. Item 3
   1. Subitem 3.1
   2. Subitem 3.2

## Links and Images

[Link Text](https://www.example.com)
![Image Alt Text](https://i.pravatar.cc/150?img=4)

## Blockquotes

> This is a blockquote.
> - Anonymous

## Code

\`\`\`python
def hello_world():
    print("Hello, World!")
\`\`\`

## Tables

| Header 1 | Header 2 | Header 3 |
| -------- | -------- | -------- |
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |

## Horizontal Rule

---

## Escaping Characters

\\\*This text is not italic\\\*

## Task Lists

- [x] Task 1
- [ ] Task 2
- [ ] Task 3

## Emojis

:smile: :thumbsup: :rocket:

## HTML Elements

<details>
  <summary>Click to Expand</summary>
  <p>This is hidden text.</p>
</details>
<script>
alert("fuck")
<\/script>
`;
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

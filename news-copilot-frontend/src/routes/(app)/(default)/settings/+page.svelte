<script>
	import { AccordionItem, Accordion } from 'flowbite-svelte';
</script>

<Accordion
	activeClasses="bg-blue-100 dark:bg-gray-800 text-blue-600 dark:text-white focus:ring-4 focus:ring-blue-200 dark:focus:ring-blue-800"
	inactiveClasses="text-gray-500 dark:text-gray-400 hover:bg-blue-100 dark:hover:bg-gray-800"
	class="my-12"
>
	<AccordionItem class="mx-auto w-1/2">
		<span slot="header">Size</span>
		<p class="mb-2 text-center text-gray-500 dark:text-gray-400">
			Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo ab necessitatibus sint
			explicabo ...
		</p>
	</AccordionItem>
	<AccordionItem class="mx-auto w-1/2">
		<span slot="header">Password</span>
		<p class="mb-2 text-center text-gray-500 dark:text-gray-400">
			Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo ab necessitatibus sint
			explicabo ...
		</p>
	</AccordionItem>
	<AccordionItem class="mx-auto w-1/2">
		<span slot="header">Abc</span>
		<p class="mb-2 text-center text-gray-500 dark:text-gray-400">
			Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo ab necessitatibus sint
			explicabo ...
		</p>
	</AccordionItem>
	<AccordionItem class="mx-auto w-1/2">
		<span slot="header">Color</span>
		<p class="mb-2 text-center text-gray-500 dark:text-gray-400">
			Lorem ipsum dolor sit amet, consectetur adipisicing elit. Illo ab necessitatibus sint
			explicabo ...
		</p>
	</AccordionItem>
</Accordion>

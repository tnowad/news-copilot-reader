<script lang="ts">
	import { Section } from 'flowbite-svelte-blocks';
	import { FooterCopyright } from 'flowbite-svelte';
</script>

<Section name="testimonial">
	<h1 class="mb-4 text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">
		Licensing Information
	</h1>
	<p class="mb-1 font-light text-gray-500 dark:text-gray-400 sm:text-xl lg:mb-12">
		This website provides news content and utilizes AI-powered autocorrect technology to enhance
		accuracy and clarity.
	</p>
	<h1 class="mb-4 text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">
		Content Licensing
	</h1>
	<p>
		News Content: Licensed under <a
			href="https://creativecommons.org/licenses/by/4.0/"
			target="_blank"
			rel="noopener noreferrer">Creative Commons Attribution (CC BY)</a
		>.
	</p>
	<p class="lg:mb-12">
		AI-Generated AutoCorrecter : Licensed under <a
			href="https://creativecommons.org/licenses/by-nc-sa/4.0/"
			target="_blank"
			rel="noopener noreferrer"
			>Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA)</a
		>.
	</p>
	<h1 class="mb-4 text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">
		Copyright
	</h1>
	<FooterCopyright href="/" by="News Copilot™" />
</Section>

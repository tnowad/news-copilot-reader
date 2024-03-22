<script>
	import { Section, News, HeroHeader, HeroBody } from 'flowbite-svelte-blocks';
	import { Button } from 'flowbite-svelte';
	import { ArrowRightOutline, VideoCameraSolid } from 'flowbite-svelte-icons';
	//import { Youtube, ProductHunt, Reddit } from '../utils';
</script>

<br />
<Section name="heroDefault">
	<HeroHeader>
		<svelte:fragment slot="h1">About Us: News Copilot</svelte:fragment>
		<svelte:fragment slot="paragraph"
			>Welcome to News Copilot, your trusted source for in-depth and unbiased news coverage from
			around the world .</svelte:fragment
		>
	</HeroHeader>
	<br />
	<div
		class="mb-8 flex flex-col space-y-4 sm:flex-row sm:justify-center sm:space-x-4 sm:space-y-0 lg:mb-16"
	>
		<a href="/">
			<Button size="lg" color="red">
				Learn more <ArrowRightOutline size="md" class="-mr-1 ml-2" />
			</Button>
		</a>
		<a href="/"> </a>
	</div></Section
>

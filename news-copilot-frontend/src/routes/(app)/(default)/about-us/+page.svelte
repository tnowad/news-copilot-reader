<script>
    import { Section, News, HeroHeader, HeroBody } from 'flowbite-svelte-blocks';
    import { Button } from 'flowbite-svelte';
    import { ArrowRightOutline, VideoCameraSolid } from 'flowbite-svelte-icons';
    //import { Youtube, ProductHunt, Reddit } from '../utils';
  </script>
  <br>
  <Section name="heroDefault">
   
    <HeroHeader>
      <svelte:fragment slot="h1">About Us:  News Copilot  </svelte:fragment>
      <svelte:fragment slot="paragraph">Welcome to News Copilot, your trusted source for in-depth and unbiased news coverage from around the world .</svelte:fragment>
    </HeroHeader>
    <br>
    <div class="flex flex-col mb-8 lg:mb-16 space-y-4 sm:flex-row sm:justify-center sm:space-y-0 sm:space-x-4">
      <a href="/">
        <Button size="lg" color="red">
          Learn more <ArrowRightOutline size="md" class="ml-2 -mr-1" />
        </Button>
      </a>
      <a href="/">
     
  </Section>
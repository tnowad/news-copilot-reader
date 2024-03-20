<script lang="ts">
	import { Page404, Page500 } from 'flowbite-svelte-blocks';
	import { Button } from 'flowbite-svelte';
	import { page } from '$app/stores';
	import { StatusCodes } from 'http-status-codes';
</script>

<div class="flex h-screen items-center justify-center">
	{#if $page.status === StatusCodes.NOT_FOUND}
		<Page404>
			<svelte:fragment slot="h1">404 🙁</svelte:fragment>
			<svelte:fragment slot="paragraph">
				<p class="mb-4 text-3xl font-bold tracking-tight text-gray-900 dark:text-white md:text-4xl">
					Not Found
				</p>
				<p class="mb-4 text-lg font-light text-gray-500 dark:text-gray-400">
					Sorry, we can't find that page. You'll find lots to explore on the home page.
				</p>
				<Button href="/" size="lg" color="red">Back to Homepage</Button>
			</svelte:fragment>
		</Page404>
	{:else if $page.status === StatusCodes.INTERNAL_SERVER_ERROR}
		<Page500>
			<svelte:fragment slot="h1">500 💥</svelte:fragment>
			<svelte:fragment slot="paragraph">
				<p class="mb-4 text-3xl font-bold tracking-tight text-gray-900 dark:text-white md:text-4xl">
					Internal Server Error.
				</p>
				<p class="mb-4 text-lg font-light text-gray-500 dark:text-gray-400">
					We are already working to solve the problem.
				</p>
				<Button href="/" size="lg" color="red">Back to Homepage</Button>
			</svelte:fragment>
		</Page500>
	{/if}
</div>

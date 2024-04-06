<script context="module" lang="ts">
	import { load } from './+page.ts'; // Importing load function from your router file

	export async function loadPage({ request }) {
		return load(request); // Calling the load function to fetch comments
	}
</script>

<script lang="ts">
	export let comments = [];
	export let metadata = null;

	function nextPage() {
		// Navigate to the next page
		// You need to implement your own navigation logic
		console.log('Next page');
	}

	function previousPage() {
		// Navigate to the previous page
		// You need to implement your own navigation logic
		console.log('Previous page');
	}
</script>

<main>
	<section>
		<h2>Comments</h2>
		<ul>
			{#each comments as comment}
				<li>{comment.content} - {comment.author.name}</li>
			{/each}
		</ul>
	</section>

	<section>
		<p>Page: {metadata?.currentPage}/{metadata?.totalPages}</p>
		<button on:click={previousPage} disabled={metadata?.currentPage === 1}>Previous</button>
		<button on:click={nextPage} disabled={metadata?.currentPage === metadata?.totalPages}
			>Next</button
		>
	</section>
</main>

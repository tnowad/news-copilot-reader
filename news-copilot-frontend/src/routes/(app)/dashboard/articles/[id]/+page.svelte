<script lang="ts">
	export let article;
	export let comments;

	let newComment = '';

	async function addComment() {
		const response = await fetch(`api/articles/${$article.id}/comments`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ content: newComment })
		});

		if (response.ok) {
			// Refresh comments
			// You may choose to reload the entire page or just fetch the comments again
			// Example: loadPage({ params: { id: $article.id } });
			newComment = ''; // Clear the input field
		} else {
			console.error('Failed to add comment');
		}
	}
</script>

<main>
	{#if article}
		<article>
			<h1>{article.title}</h1>
			<p>{article.content}</p>
		</article>

		<section>
			<h2>Comments</h2>
			<ul>
				{#each comments as comment}
					<li>{comment.content}</li>
				{/each}
			</ul>
		</section>

		<section>
			<h2>Add a Comment</h2>
			<textarea bind:value={newComment}></textarea>
			<button on:click={addComment}>Add Comment</button>
		</section>
	{:else}
		<p>Loading...</p>
	{/if}
</main>

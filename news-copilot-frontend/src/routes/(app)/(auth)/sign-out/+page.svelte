<script>
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import { Button, Modal } from 'flowbite-svelte';
	let defaultModal = true;

	$: defaultModal === false && goto('/');
</script>

<Modal title="Are you sure you want to sign out?" bind:open={defaultModal}>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
		By signing out, you will be logged out of your account.
	</p>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">Do you wish to proceed?</p>
	<form action="/sign-out" method="post" use:enhance>
		<Button type="submit">Sign Out</Button>
		<Button type="button" on:click={() => (defaultModal = false)}>Cancel</Button>
	</form>
</Modal>

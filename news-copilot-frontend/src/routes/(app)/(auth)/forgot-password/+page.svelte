<script lang="ts">
	import { Section, Register } from 'flowbite-svelte-blocks';
	import { Button, Label, Input } from 'flowbite-svelte';
	import { enhance } from '$app/forms';
	import type { ActionData } from './$types';
	import { getErrorFieldMessage } from '$lib/utils/form';
	import { StatusCodes } from 'http-status-codes';
	import { toasts } from 'svelte-toasts';
	import { goto } from '$app/navigation';

	export let form: ActionData;

	$: if (form?.statusCode === StatusCodes.OK) {
		toasts.success(form.message ?? 'You have successfully signed in');
		goto(form.redirectTo ?? '/');
	} else if (form?.statusCode === StatusCodes.UNPROCESSABLE_ENTITY) {
		toasts.error(form?.message ?? 'Invalid email or password');
	}
</script>

<Section name="login" sectionClass="w-full md:w-[500px]">
	<Register href="/">
		<svelte:fragment slot="top">
			<img class="mr-2 h-8 w-8" src="/images/logo.png" alt="logo" />
			News Copilot
		</svelte:fragment>

		<div class="space-y-4 p-6 sm:p-8 md:space-y-6">
			<form class="flex flex-col space-y-6" action="/forgot-password" method="post" use:enhance>
				<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Forgot Password</h3>
				<Label class="space-y-2">
					<span>Your email</span>
					<Input type="email" name="email" placeholder="name@email.com" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'email')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'email')}</p>
					{/if}
				</Label>
				<Button type="submit" class="w-full">Send Reset Code</Button>
				<p class="text-sm font-light text-gray-500 dark:text-gray-400">
					Don’t have an account yet? <a
						href="/sign-up"
						class="font-medium text-primary-600 hover:underline dark:text-primary-500">Sign up</a
					>
				</p>
			</form>
		</div>
	</Register>
</Section>

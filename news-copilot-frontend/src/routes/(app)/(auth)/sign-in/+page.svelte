<script lang="ts">
	import { Section, Register } from 'flowbite-svelte-blocks';
	import { Button, Checkbox, Label, Input } from 'flowbite-svelte';
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
	} else if (form?.statusCode === StatusCodes.UNAUTHORIZED) {
		toasts.error(form?.message ?? 'Invalid email or password');
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
			<form class="flex flex-col space-y-6" action="/sign-in" method="post" use:enhance>
				<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Sign In</h3>
				<Label class="space-y-2">
					<span>Your email</span>
					<Input type="email" name="email" placeholder="name@email.com" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'email')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'email')}</p>
					{/if}
				</Label>
				<Label class="space-y-2">
					<span>Your password</span>
					<Input type="password" name="password" placeholder="••••••••" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'password')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'password')}</p>
					{/if}
				</Label>
				<div class="flex items-start">
					<Checkbox name="remember">Remember me</Checkbox>
					<a href="/" class="ml-auto text-sm text-blue-700 hover:underline dark:text-blue-500"
						>Forgot password?</a
					>
				</div>
				<Button type="submit" class="w-full1">Sign in</Button>
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

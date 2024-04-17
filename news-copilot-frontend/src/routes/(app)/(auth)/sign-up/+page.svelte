<script lang="ts">
	import { Section, Register } from 'flowbite-svelte-blocks';
	import { Button, Label, Input, Checkbox } from 'flowbite-svelte';
	import { getErrorFieldMessage } from '$lib/utils/form';
	import type { ActionData } from './$types';
	import { goto } from '$app/navigation';
	import { StatusCodes } from 'http-status-codes';
	import { toasts } from 'svelte-toasts';

	export let form: ActionData;
	$: if (form?.statusCode === StatusCodes.CREATED) {
		toasts.success(form.message ?? 'You have successfully signed up');
		goto(form?.redirectTo ?? '/');
	} else if (
		form?.statusCode === StatusCodes.BAD_REQUEST ||
		form?.statusCode === StatusCodes.CONFLICT
	) {
		toasts.error(form?.message ?? 'Could not sign up. Please try again.');
	} else if (form?.statusCode === StatusCodes.UNPROCESSABLE_ENTITY) {
		toasts.error(form?.message ?? 'Invalid form data. Please check the form and try again.');
	}
</script>

<Section name="register" sectionClass="w-full md:w-[500px]">
	<Register href="/">
		<svelte:fragment slot="top">
			<img class="mr-2 h-8 w-8" src="/images/logo.png" alt="logo" />
			News Copilot
		</svelte:fragment>
		<div class="space-y-4 p-6 sm:p-8 md:space-y-6">
			<form class="flex flex-col space-y-6" action="/sign-up" method="post">
				<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Sign Up</h3>
				<Label class="space-y-2">
					<span>Your email</span>
					<Input type="email" name="email" placeholder="name@email.com" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'email')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'email')}</p>
					{/if}
				</Label>
				<Label class="space-y-2">
					<span>Display Name</span>
					<Input type="text" name="displayName" placeholder="Your Display Name" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'displayName')}
						<p class="mt-1 text-xs text-red-500">
							{getErrorFieldMessage(form.errors, 'displayName')}
						</p>
					{/if}
				</Label>
				<Label class="space-y-2">
					<span>Create password</span>
					<Input type="password" name="password" placeholder="••••••••" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'password')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'password')}</p>
					{/if}
				</Label>
				<Label class="space-y-2">
					<span>Confirm password</span>
					<Input type="password" name="confirmPassword" placeholder="••••••••" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'confirmPassword')}
						<p class="mt-1 text-xs text-red-500">
							{getErrorFieldMessage(form.errors, 'confirmPassword')}
						</p>
					{/if}
				</Label>
				<div class="flex flex-col items-start">
					<Checkbox name="acceptTerms" required
						>I accept the <a
							class="font-medium text-primary-600 hover:underline dark:text-primary-500"
							href="/"
						>
							Terms and Conditions</a
						></Checkbox
					>
					{#if form?.errors && getErrorFieldMessage(form.errors, 'acceptTerms')}
						<p class="mt-1 text-xs text-red-500">
							{getErrorFieldMessage(form.errors, 'acceptTerms')}
						</p>
					{/if}
				</div>
				<Button type="submit" class="w-full">Sign Up</Button>
				<p class="text-sm font-light text-gray-500 dark:text-gray-400">
					Already have an account? <a
						href="/sign-in"
						class="font-medium text-primary-600 hover:underline dark:text-primary-500">Sign In</a
					>
				</p>
			</form>
		</div>
	</Register>
</Section>

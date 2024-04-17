<script lang="ts">
	import { Section, Register } from 'flowbite-svelte-blocks';
	import { Button, Checkbox, Label, Input } from 'flowbite-svelte';
	import { enhance } from '$app/forms';
	import type { ActionData, PageData } from './$types';
	import { getErrorFieldMessage } from '$lib/utils/form';
	import { StatusCodes } from 'http-status-codes';
	import { toasts } from 'svelte-toasts';
	import { goto } from '$app/navigation';

	export let form: ActionData;
	export let data: PageData;

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
			<form class="flex flex-col space-y-6" action="/reset-password" method="post" use:enhance>
				<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Reset Password</h3>
				<Label class="space-y-2" defaultClass="hidden">
					<span>Your email</span>
					<Input
						type="email"
						name="email"
						placeholder="name@email.com"
						value={data.email}
						required
					/>
					{#if form?.errors && getErrorFieldMessage(form.errors, 'email')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'email')}</p>
					{/if}
				</Label>
				<Label class="space-y-2">
					<span>Reset Password Code</span>
					<Input type="number" name="code" placeholder="000000" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'code')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'code')}</p>
					{/if}
				</Label>

				<Label class="space-y-2">
					<span>New password</span>
					<Input type="password" name="password" placeholder="••••••••" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'password')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'password')}</p>
					{/if}
				</Label>

				<Label class="space-y-2">
					<span>Confirm new password</span>
					<Input type="password" name="confirmPassword" placeholder="••••••••" required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'confirmPassword')}
						<p class="mt-1 text-xs text-red-500">
							{getErrorFieldMessage(form.errors, 'confirmPassword')}
						</p>
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

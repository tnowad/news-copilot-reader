<script lang="ts">
	import { Section, Register } from 'flowbite-svelte-blocks';
	import { Button, Label, Input, Checkbox } from 'flowbite-svelte';
	import { getErrorFieldMessage } from '$lib/utils/form';
	import type { ActionData } from './$types';
	import { goto } from '$app/navigation';
	import { StatusCodes } from 'http-status-codes';
	import { toasts } from 'svelte-toasts';
	import { _ } from 'svelte-i18n';

	export let form: ActionData;

	$: if (form?.statusCode === StatusCodes.CREATED) {
		toasts.success(form.message ?? $_('sign-up.messages.success'));
		goto(form.redirectTo ?? '/');
	} else if (
		form?.statusCode === StatusCodes.BAD_REQUEST ||
		form?.statusCode === StatusCodes.CONFLICT
	) {
		toasts.error(form?.message ?? $_('sign-up.messages.error-existing-account'));
	} else if (form?.statusCode === StatusCodes.UNPROCESSABLE_ENTITY) {
		toasts.error(form?.message ?? $_('sign-up.messages.error-invalid-form-data'));
	}
</script>

<Section name="register" sectionClass="w-full md:w-[500px]">
	<Register href="/">
		<svelte:fragment slot="top">
			<img class="mr-2 h-8 w-8" src="/images/logo.png" alt="logo" />
			{$_('common.app-name')}
		</svelte:fragment>
		<div class="space-y-4 p-6 sm:p-8 md:space-y-6">
			<form class="flex flex-col space-y-6" action="/sign-up" method="post">
				<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">
					{$_('sign-up.page-title')}
				</h3>
				<Label class="space-y-2">
					<span>{$_('sign-up.labels.email')}</span>
					<Input
						type="email"
						name="email"
						placeholder={$_('sign-up.placeholders.email')}
						required
					/>
					{#if form?.errors && getErrorFieldMessage(form.errors, 'email')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'email')}</p>
					{/if}
				</Label>
				<Label class="space-y-2">
					<span>{$_('sign-up.labels.name')}</span>
					<Input type="text" name="name" placeholder={$_('sign-up.placeholders.name')} required />
					{#if form?.errors && getErrorFieldMessage(form.errors, 'name')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'name')}</p>
					{/if}
				</Label>
				<Label class="space-y-2">
					<span>{$_('sign-up.labels.password')}</span>
					<Input
						type="password"
						name="password"
						placeholder={$_('sign-up.placeholders.password')}
						required
					/>
					{#if form?.errors && getErrorFieldMessage(form.errors, 'password')}
						<p class="mt-1 text-xs text-red-500">{getErrorFieldMessage(form.errors, 'password')}</p>
					{/if}
				</Label>
				<Label class="space-y-2">
					<span>{$_('sign-up.labels.confirm-password')}</span>
					<Input
						type="password"
						name="confirmPassword"
						placeholder={$_('sign-up.placeholders.confirm-password')}
						required
					/>
					{#if form?.errors && getErrorFieldMessage(form.errors, 'confirmPassword')}
						<p class="mt-1 text-xs text-red-500">
							{getErrorFieldMessage(form.errors, 'confirmPassword')}
						</p>
					{/if}
				</Label>
				<div class="flex flex-col items-start">
					<Checkbox name="acceptTerms" required class="space-x-1">
						{$_('sign-up.labels.accept-terms')}
						<a href="/" class="font-medium text-primary-600 hover:underline dark:text-primary-500">
							{$_('sign-up.labels.terms-and-conditions')}
						</a>
					</Checkbox>
					{#if form?.errors && getErrorFieldMessage(form.errors, 'acceptTerms')}
						<p class="mt-1 text-xs text-red-500">
							{getErrorFieldMessage(form.errors, 'acceptTerms')}
						</p>
					{/if}
				</div>
				<Button type="submit" class="w-full">{$_('sign-up.buttons.sign-up')}</Button>
				<p class="text-sm font-light text-gray-500 dark:text-gray-400">
					{$_('sign-up.links.already-have-account')}
					<a
						href="/sign-in"
						class="font-medium text-primary-600 hover:underline dark:text-primary-500"
						>{$_('sign-up.links.sign-in')}</a
					>
				</p>
			</form>
		</div>
	</Register>
</Section>

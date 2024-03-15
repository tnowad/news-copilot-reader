<script lang="ts">
	import { Section, Register } from 'flowbite-svelte-blocks';
	import { Button, Label, Input } from 'flowbite-svelte';
</script>

<Section name="register" sectionClass="w-full md:w-[500px]">
	<Register href="/">
		<svelte:fragment slot="top">
			<img class="w-8 h-8 mr-2" src="/images/logo.png" alt="logo" />
			News Copilot
		</svelte:fragment>
		<div class="p-6 space-y-4 md:space-y-6 sm:p-8">
			<form class="flex flex-col space-y-6" action="/">
				<h3 class="text-xl font-medium text-gray-900 dark:text-white p-0">Sign Up</h3>
				<Label class="space-y-2">
					<span>Your email</span>
					<Input type="email" name="email" placeholder="name@email.com" required />
				</Label>
				<Label class="space-y-2">
					<span>Create password</span>
					<Input type="password" name="password" placeholder="••••••••" required />
				</Label>
				<Label class="space-y-2">
					<span>Confirm password</span>
					<Input type="password" name="confirmPassword" placeholder="••••••••" required />
				</Label>
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

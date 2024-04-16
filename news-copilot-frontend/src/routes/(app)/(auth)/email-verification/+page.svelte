<script lang="ts">
	import { Card, Button, Label, Input, Checkbox } from 'flowbite-svelte';
</script>

<Card>
	<form class="flex flex-col space-y-6" action="/">
		<h3 class="text-center text-xl font-medium text-gray-900 dark:text-white">
			VERIFICATION EMAIL
		</h3>
		<Label class="space-y-2">
			<span>Email</span>
			<Input type="email" name="email" placeholder="name@company.com" required />
		</Label>

		<div class="flex items-start">
			<Checkbox>You are not a robot</Checkbox>
		</div>
		<Button type="submit" class="w-full">Submit</Button>
		<div class="text-sm font-medium text-gray-500 dark:text-gray-300">
			Not registered? <a
				href="/sign-up"
				class="text-primary-700 hover:underline dark:text-primary-500"
			>
				Create account
			</a>
		</div>
	</form>
</Card>

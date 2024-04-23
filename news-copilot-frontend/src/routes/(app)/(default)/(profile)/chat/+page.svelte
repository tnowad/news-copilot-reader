<script lang="ts">
	import { Section } from 'flowbite-svelte-blocks';
	import { Label, Input } from 'flowbite-svelte';
</script>

<section class="w-full">
	<div class="anwser">
		<div class="mb-6">
			<Label for="default-input" class="mb-2 block">message1</Label>
			<Input id="default-input" placeholder="Default input" disabled value="Disabled input" />
		</div>
		<div class="mb-6">
			<Label for="default-input" class="mb-2 block">message2</Label>
			<Input id="default-input" placeholder="Default input" disabled value="Disabled input" />
		</div>
		<div class="mb-6">
			<Label for="default-input" class="mb-2 block">message2</Label>
			<Input id="default-input" placeholder="Default input" disabled value="Disabled input" />
		</div>
		<div class="mb-6">
			<Label for="default-input" class="mb-2 block">message2</Label>
			<Input id="default-input" placeholder="Default input" disabled value="Disabled input" />
		</div>
		<div class="mb-6">
			<Label for="default-input" class="mb-2 block">message2</Label>
			<Input id="default-input" placeholder="Default input" disabled value="Disabled input" />
		</div>
		<div class="mb-6">
			<Label for="default-input" class="mb-2 block">message2</Label>
			<Input id="default-input" placeholder="Default input" disabled value="Disabled input" />
		</div>
		<div class="mb-6">
			<Label for="default-input" class="mb-2 block">message2</Label>
			<Input id="default-input" placeholder="Default input" disabled value="Disabled input" />
		</div>
	</div>
	<div class="relative mb-6 mt-20 w-full">
		<Input class="absolute bottom-0 left-0" id="default-input" placeholder="Message chatbot" />
	</div>
</section>

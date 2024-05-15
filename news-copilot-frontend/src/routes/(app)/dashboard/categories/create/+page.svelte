<script lang="ts">
	import { Section } from 'flowbite-svelte-blocks';
	import { Button, Input, Label, Select, Textarea } from 'flowbite-svelte';

	export let data;
</script>

<section>
	<form action={`/dashboard/categories/create`} method="post">
		<div class="mb-4 grid gap-4 sm:grid-cols-2">
			<div>
				<Label for="name" class="mb-2">Title</Label>
				<Input type="text" id="title" placeholder="" required name="title" />
			</div>
			<div>
				<Label for="brand" class="mb-2">Slug</Label>
				<Input type="text" id="slug" placeholder="" required name="slug" />
			</div>
			<div class="sm:col-span-2">
				<Label for="description" class="mb-2">Description</Label>
				<Textarea
					id="description"
					placeholder="Your description here"
					rows="4"
					name="description"
					required
				/>
			</div>
			<div class="flex items-center space-x-4">
				<Button type="submit" class="w-64">Create Category</Button>
			</div>
		</div>
	</form>
</section>

<script lang="ts">
	import { Section } from 'flowbite-svelte-blocks';
	import { Button, Input, Label, Select, Textarea } from 'flowbite-svelte';

	export let data;
</script>

<section>
	<form>
		<div class="mb-4 grid gap-4 sm:grid-cols-2">
			<div class="sm:col-span-2">
				<Label for="description" class="mb-2">Description</Label>
				<Textarea
					id="description"
					placeholder="Your description here"
					rows="4"
					name="description"
					required
					value={data.comment?.content}
				/>
			</div>
			<div class="flex items-center space-x-4">
				<Button type="submit" class="w-64">Update Comment</Button>
			</div>
		</div>
	</form>
</section>

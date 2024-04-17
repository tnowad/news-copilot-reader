<script lang="ts">
	import { Section } from 'flowbite-svelte-blocks';
	import {
		Breadcrumb,
		BreadcrumbItem,
		Button,
		Input,
		Label,
		Select,
		Textarea
	} from 'flowbite-svelte';

	export let data;
</script>

<section>
	<div>
		<Breadcrumb class="mb-6">
			<BreadcrumbItem home>Home</BreadcrumbItem>
			<BreadcrumbItem
				class="inline-flex items-center text-gray-700 hover:text-primary-600 dark:text-gray-300 dark:hover:text-white"
				href="/dashboard/comments">Comments</BreadcrumbItem
			>
			<BreadcrumbItem>{data.comment.id}</BreadcrumbItem>
		</Breadcrumb>
	</div>
</section>

<section>
	<form>
		<div class="mb-4 grid gap-4 sm:grid-cols-2">
			<div class="sm:col-span-2">
				<Label for="description" class="mb-2">Description</Label>
				<input type="hidden" name="id" value={data.comment?.id} />
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

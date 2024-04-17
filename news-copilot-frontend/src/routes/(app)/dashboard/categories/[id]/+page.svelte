<script lang="ts">
	import { Breadcrumb, BreadcrumbItem, Button, Input, Label, Textarea } from 'flowbite-svelte';

	export let data;
</script>

<section>
	<div>
		<Breadcrumb class="mb-6">
			<BreadcrumbItem home>Home</BreadcrumbItem>
			<BreadcrumbItem
				class="inline-flex items-center text-gray-700 hover:text-primary-600 dark:text-gray-300 dark:hover:text-white"
				href="/dashboard/categories">Categories</BreadcrumbItem
			>
			<BreadcrumbItem>{data.category?.title}</BreadcrumbItem>
		</Breadcrumb>
	</div>
</section>

<section>
	<form action={`/dashboard/categories/${data.category?.id}`} method="post">
		<div class="mb-4 grid gap-4 sm:grid-cols-2">
			<div>
				<Label for="name" class="mb-2">Title</Label>
				<Input
					type="text"
					id="title"
					placeholder=""
					value={data.category?.title}
					required
					name="title"
				/>
			</div>
			<div>
				<Label for="brand" class="mb-2">Slug</Label>
				<Input
					type="text"
					id="slug"
					placeholder=""
					value={data.category?.slug}
					required
					name="slug"
				/>
			</div>
			<div class="sm:col-span-2">
				<Label for="description" class="mb-2">Description</Label>
				<Textarea
					id="description"
					placeholder="Your description here"
					rows="4"
					name="description"
					required
					value={data.category?.description}
				/>
			</div>
			<div class="flex items-center space-x-4">
				<Button type="submit" class="w-64">Update product</Button>
			</div>
		</div>
	</form>
</section>

<script lang="ts">
	import {
		Chart,
		Card,
		TableHead,
		TableHeadCell,
		TableBodyRow,
		TableBody,
		TableBodyCell,
		Badge
	} from 'flowbite-svelte';
	import { Section, Social } from 'flowbite-svelte-blocks';
	export let data;
	$: console.log(data);
</script>

<section class="h-full w-full">
	<div class="container grid h-full w-auto grid-cols-12 gap-2">
		<Card class="col-span-6" size="none">
			<Chart class="w-full" options={data.categoryArticleCount} />
		</Card>
		<Card class="col-span-6" size="none">
			<Social>
				<div class="flex flex-col items-center justify-center">
					<dt class="mb-2 text-3xl font-extrabold md:text-4xl">
						{data.articlesStatistics?.totalArticles}
					</dt>
					<dd class="font-light text-gray-500 dark:text-gray-400">Articles</dd>
				</div>
				<div class="flex flex-col items-center justify-center">
					<dt class="mb-2 text-3xl font-extrabold md:text-4xl">
						{data.articlesStatistics?.totalUser}
					</dt>
					<dd class="font-light text-gray-500 dark:text-gray-400">Users</dd>
				</div>
				<div class="flex flex-col items-center justify-center">
					<dt class="mb-2 text-3xl font-extrabold md:text-4xl">
						{data.articlesStatistics?.totalCategories}
					</dt>
					<dd class="font-light text-gray-500 dark:text-gray-400">Categories</dd>
				</div>
			</Social>
		</Card>
		<Card class="col-span-12" size="none">
			<TableHead>
				<TableHeadCell padding="px-4 py-3" scope="col">ID</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Title</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Author</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Categories</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Summary</TableHeadCell>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each data.articles as article (article.id)}
					<TableBodyRow>
						<TableBodyCell tdClass="px-4 py-3">{article.id}</TableBodyCell>
						<a href={`/dashboard/articles/${article.id}`}>
							<TableBodyCell tdClass="px-4 py-3">{article.title}</TableBodyCell>
						</a>
						<TableBodyCell tdClass="px-4 py-3">{article.author?.email}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3"
							>{#each article.categories ?? [] as category (category.id)}
								<Badge>{category.title}</Badge>
							{/each}</TableBodyCell
						>
						<TableBodyCell tdClass="px-4 py-3">{article.summary}</TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
		</Card>
	</div>
</section>
<br />

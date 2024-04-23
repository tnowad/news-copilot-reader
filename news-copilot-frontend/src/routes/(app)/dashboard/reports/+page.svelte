<script lang="ts">
	import { enhance } from '$app/forms';
	import {
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		TableSearch,
		Button,
		Dropdown,
		DropdownItem,
		Checkbox,
		ButtonGroup,
		Badge,
		Input,
		Breadcrumb,
		BreadcrumbItem
	} from 'flowbite-svelte';
	import { Section } from 'flowbite-svelte-blocks';
	import {
		PlusOutline,
		ChevronDownOutline,
		FilterSolid,
		ChevronRightOutline,
		ChevronLeftOutline
	} from 'flowbite-svelte-icons';
	import type { PageData } from './$types';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import type { ActionData } from '../$types';
	import { toasts } from 'svelte-toasts';

	export let data: PageData;
	let page = +(data.metadata?.pagination.currentPage ?? 1);
	let limit = +(data.metadata?.pagination.limit ?? 10);
	let searchQuery = data.metadata && data.metadata.filters ? data.metadata.filters.search : '';

	const gotoPage = (
		nextPage: number = page,
		nextLimit: number = limit,
		nextSearch: string = searchQuery
	) => {
		if (!browser) {
			return;
		}
		const url = new URL(window.location.href);
		url.searchParams.set('page', nextPage + '');
		url.searchParams.set('limit', nextLimit + '');
		url.searchParams.set('search', nextSearch);

		goto(url.toString(), {
			noScroll: true,
			keepFocus: true
		});
	};

	let debounceId: number;
	const debounce = (fn: () => void, time: number) => {
		if (debounceId) {
			clearTimeout(debounceId);
		}
		debounceId = setTimeout(() => {
			fn();
		}, time) as unknown as number;
	};

	$: debounce(() => {
		gotoPage(page, limit, searchQuery);
	}, 100);

	export let form: ActionData;
	$: {
		if (form) {
			if (form.statusCode >= 200 && form.statusCode < 300) {
				toasts.success(form.message);
			} else {
				toasts.error(form.message);
			}
		}
	}
</script>

<section>
	<div>
		<Breadcrumb class="mb-6">
			<BreadcrumbItem home>Home</BreadcrumbItem>
			<BreadcrumbItem
				class="hover:text-primary-600 inline-flex items-center text-gray-700 dark:text-gray-300 dark:hover:text-white"
				href="/dashboard/categories">Reports</BreadcrumbItem
			>
		</Breadcrumb>
	</div>
</section>

<Section sectionClass="" classDiv="max-w-none !p-0">
	<form method="get" action="/dashboard/reports">
		<TableSearch
			placeholder="Search"
			hoverable={true}
			bind:inputValue={searchQuery}
			divClass="bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden"
			innerDivClass="flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0 md:space-x-4 p-4"
			searchClass="w-full md:w-1/2 relative"
			classInput="text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2  pl-10"
		>
			<div
				slot="header"
				class="flex w-full flex-shrink-0 flex-col items-stretch justify-end space-y-2 md:w-auto md:flex-row md:items-center md:space-x-3 md:space-y-0"
			>
				<Button color="alternative">Actions<ChevronDownOutline class="ml-2 h-3 w-3 " /></Button>
				<Dropdown class="w-20 divide-y divide-gray-100">
					<DropdownItem>
						<a href="/dashboard/reports/create">create</a>
					</DropdownItem>
				</Dropdown>
			</div>
			<TableHead>
				<TableHeadCell padding="px-4 py-3" scope="col">ID</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Type</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">ObjectId</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Description</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Actions</TableHeadCell>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each data.reports as report (report.id)}
					<TableBodyRow>
						<TableBodyCell tdClass="px-4 py-3">{report.id}</TableBodyCell>
						{#if report.objectType == 'Article'}
							<a href={`/dashboard/articles/${report.objectId}`}>
								<TableBodyCell tdClass="px-4 py-3">{report.objectType}</TableBodyCell>
							</a>
						{:else if report.objectType == 'User'}
							<a href={`/dashboard/users/${report.objectId}`}>
								<TableBodyCell tdClass="px-4 py-3">{report.objectType}</TableBodyCell>
							</a>
						{:else}
							<!-- dashboard/comments/[id] is not implemented yet-->
							<a href={`/dashboard/comments/${report.objectId}`}>
								<TableBodyCell tdClass="px-4 py-3">{report.objectType}</TableBodyCell>
							</a>
						{/if}
						<TableBodyCell tdClass="px-4 py-3">{report.objectId}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{report.content}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">
							<form use:enhance method="post" action="/dashboard/reports?/deleteReport">
								<input type="hidden" name="reportId" value={report.id} />
								<Button outline color="red" type="submit">Delete</Button>
							</form>
						</TableBodyCell>
					</TableBodyRow>
				{/each}
			</TableBody>
			<div
				slot="footer"
				class="flex flex-col items-start justify-between space-y-3 p-4 md:flex-row md:items-center md:space-y-0"
				aria-label="Table navigation"
			>
				{#if data.metadata}
					<span class="text-sm font-normal text-gray-500 dark:text-gray-400">
						Showing
						<span class="font-semibold text-gray-900 dark:text-white"
							>{data.metadata.pagination.offset}-{data.metadata.pagination.nextOffset}</span
						>
						of
						<span class="font-semibold text-gray-900 dark:text-white"
							>{data.metadata.pagination.totalCount}</span
						>
					</span>
					<ButtonGroup>
						<Button
							on:click={() => {
								if (data.metadata && !(+data.metadata.pagination.currentPage <= 1)) {
									page = page - 1;
									gotoPage(page - 1, limit);
								}
							}}><ChevronLeftOutline size="xs" class="m-1.5" /></Button
						>
						<Input
							type="number"
							name="page"
							defaultValue={page}
							bind:value={page}
							min="1"
							max={data.metadata.pagination.pageCount}
							class="w-16 text-center"
						/>
						<Button
							on:click={() => {
								if (
									data.metadata &&
									!(
										+data.metadata.pagination.currentPage >=
										+data.metadata.pagination.pageCount - 1
									)
								) {
									page = page + 1;
									gotoPage(page + 1);
								}
							}}><ChevronRightOutline size="xs" class="m-1.5" /></Button
						>
					</ButtonGroup>
				{/if}
			</div>
		</TableSearch>
	</form>
</Section>

<script lang="ts">
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
	import { enhance } from '$app/forms';

	export let data: PageData;

	let page = +(data.metadata?.pagination.currentPage ?? 1);
	let limit = +(data.metadata?.pagination.limit ?? 10);
	let searchQuery = data.metadata?.filters.search ?? '';

	const sortByField = (field: string) => {
		if (data.users && data.users.length > 0) {
			data.users = data.users.sort((a, b) => a[field].localeCompare(b[field]));
		}
	};

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
</script>

<section>
	<div>
		<Breadcrumb class="mb-6">
			<BreadcrumbItem home>Home</BreadcrumbItem>
			<BreadcrumbItem
				class="hover:text-primary-600 inline-flex items-center text-gray-700 dark:text-gray-300 dark:hover:text-white"
				href="/dashboard/users">Users</BreadcrumbItem
			>
		</Breadcrumb>
	</div>
</section>

<Section sectionClass="" classDiv="max-w-none !p-0">
	<form method="get" action="/dashboard/users">
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
				<Button href="../../../sign-up">
					<PlusOutline class="mr-2 h-3.5 w-3.5" />Add user
				</Button>
				<!-- <Button color="alternative">Actions<ChevronDownOutline class="ml-2 h-3 w-3 " /></Button>
				<Dropdown class="w-44 divide-y divide-gray-100">
					<DropdownItem>Mass Edit</DropdownItem>
					<DropdownItem>Delete all</DropdownItem>
				</Dropdown> -->
				<Button color="alternative">Filter<FilterSolid class="ml-2 h-3 w-3 " /></Button>
				<Dropdown class="w-48 space-y-2 p-3 text-sm">
					<h6 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">Sort By</h6>
					<li>
						<Checkbox on:click={() => sortByField('email')}>Email</Checkbox>
					</li>
					<li>
						<Checkbox on:click={() => sortByField('displayName')}>First Name</Checkbox>
					</li>
				</Dropdown>
			</div>
			<TableHead>
				<TableHeadCell padding="px-4 py-3" scope="col">ID</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Display Name</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Email</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Phone Number</TableHeadCell>
				<TableHeadCell padding="px-4 py-3" scope="col">Bio</TableHeadCell>
			</TableHead>
			<TableBody tableBodyClass="divide-y">
				{#each data.users ?? [] as user (user.id)}
					<TableBodyRow>
						<TableBodyCell tdClass="px-4 py-3">{user.id}</TableBodyCell>
						<a href={`/dashboard/users/${user.id}`}>
							<TableBodyCell tdClass="px-4 py-3">{user.displayName}</TableBodyCell>
						</a>
						<TableBodyCell tdClass="px-4 py-3">{user.email}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{user.phoneNumber}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{user.bio}</TableBodyCell>
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
							>{data.metadata.pagination?.offset}-{data.metadata.pagination?.nextOffset}</span
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

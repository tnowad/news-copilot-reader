<script lang="ts">
	import { onMount } from 'svelte';
	import {
		Table,
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
		ButtonGroup
	} from 'flowbite-svelte';
	import { Section } from 'flowbite-svelte-blocks';
	// import paginationData from '../utils/advancedTable.json';
	import {
		PlusOutline,
		ChevronDownOutline,
		FilterSolid,
		ChevronRightOutline,
		ChevronLeftOutline
	} from 'flowbite-svelte-icons';
	import type { PageData } from './$types';

	const paginationData = [];

	let searchTerm = '';
	let currentPosition = 0;
	const itemsPerPage = 10;
	const showPage = 5;
	let totalPages = 0;
	let pagesToShow: number[] = [];
	let totalItems = paginationData.length;
	let startPage: number;
	let endPage: number;

	const updateDataAndPagination = () => {
		const currentPageItems = paginationData.slice(currentPosition, currentPosition + itemsPerPage);
		renderPagination(currentPageItems.length);
	};

	const loadNextPage = () => {
		if (currentPosition + itemsPerPage < paginationData.length) {
			currentPosition += itemsPerPage;
			updateDataAndPagination();
		}
	};

	const loadPreviousPage = () => {
		if (currentPosition - itemsPerPage >= 0) {
			currentPosition -= itemsPerPage;
			updateDataAndPagination();
		}
	};

	const renderPagination = () => {
		totalPages = Math.ceil(paginationData.length / itemsPerPage);
		const currentPage = Math.ceil((currentPosition + 1) / itemsPerPage);

		startPage = currentPage - Math.floor(showPage / 2);
		startPage = Math.max(1, startPage);
		endPage = Math.min(startPage + showPage - 1, totalPages);

		pagesToShow = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
	};

	const goToPage = (pageNumber: number) => {
		currentPosition = (pageNumber - 1) * itemsPerPage;
		updateDataAndPagination();
	};

	$: startRange = currentPosition + 1;
	$: endRange = Math.min(currentPosition + itemsPerPage, totalItems);

	onMount(() => {
		renderPagination();
	});

	$: currentPageItems = paginationData.slice(currentPosition, currentPosition + itemsPerPage);
	$: filteredItems = paginationData.filter(
		(item) => item.product_name.toLowerCase().indexOf(searchTerm.toLowerCase()) !== -1
	);

	export let data: PageData;
</script>

<Section sectionClass="bg-gray-50 dark:bg-gray-900 p-3 sm:p-5" classDiv="max-w-none">
	<TableSearch
		placeholder="Search"
		hoverable={true}
		bind:inputValue={searchTerm}
		divClass="bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden"
		innerDivClass="flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0 md:space-x-4 p-4"
		searchClass="w-full md:w-1/2 relative"
		classInput="text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2  pl-10"
	>
		<div
			slot="header"
			class="flex w-full flex-shrink-0 flex-col items-stretch justify-end space-y-2 md:w-auto md:flex-row md:items-center md:space-x-3 md:space-y-0"
		>
			<Button>
				<PlusOutline class="mr-2 h-3.5 w-3.5" />Add product
			</Button>
			<Button color="alternative">Actions<ChevronDownOutline class="ml-2 h-3 w-3 " /></Button>
			<Dropdown class="w-44 divide-y divide-gray-100">
				<DropdownItem>Mass Edit</DropdownItem>
				<DropdownItem>Delete all</DropdownItem>
			</Dropdown>
			<Button color="alternative">Filter<FilterSolid class="ml-2 h-3 w-3 " /></Button>
			<Dropdown class="w-48 space-y-2 p-3 text-sm">
				<h6 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">Choose brand</h6>
				<li>
					<Checkbox>Apple (56)</Checkbox>
				</li>
				<li>
					<Checkbox>Microsoft (16)</Checkbox>
				</li>
				<li>
					<Checkbox>Razor (49)</Checkbox>
				</li>
				<li>
					<Checkbox>Nikon (12)</Checkbox>
				</li>
				<li>
					<Checkbox>BenQ (74)</Checkbox>
				</li>
			</Dropdown>
		</div>
		<TableHead>
			<TableHeadCell padding="px-4 py-3" scope="col">Product name</TableHeadCell>
			<TableHeadCell padding="px-4 py-3" scope="col">Brand</TableHeadCell>
			<TableHeadCell padding="px-4 py-3" scope="col">Category</TableHeadCell>
			<TableHeadCell padding="px-4 py-3" scope="col">Price</TableHeadCell>
		</TableHead>
		<TableBody tableBodyClass="divide-y">
			{#if searchTerm !== ''}
				{#each filteredItems as item (item.id)}
					<TableBodyRow>
						<TableBodyCell tdClass="px-4 py-3">{item.product_name}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{item.brand}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{item.category}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{item.price}</TableBodyCell>
					</TableBodyRow>
				{/each}
			{:else}
				{#each currentPageItems as item (item.id)}
					<TableBodyRow>
						<TableBodyCell tdClass="px-4 py-3">{item.product_name}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{item.brand}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{item.category}</TableBodyCell>
						<TableBodyCell tdClass="px-4 py-3">{item.price}</TableBodyCell>
					</TableBodyRow>
				{/each}
			{/if}
		</TableBody>
		<div
			slot="footer"
			class="flex flex-col items-start justify-between space-y-3 p-4 md:flex-row md:items-center md:space-y-0"
			aria-label="Table navigation"
		>
			<span class="text-sm font-normal text-gray-500 dark:text-gray-400">
				Showing
				<span class="font-semibold text-gray-900 dark:text-white">{startRange}-{endRange}</span>
				of
				<span class="font-semibold text-gray-900 dark:text-white">{totalItems}</span>
			</span>
			<ButtonGroup>
				<Button on:click={loadPreviousPage} disabled={currentPosition === 0}
					><ChevronLeftOutline size="xs" class="m-1.5" /></Button
				>
				{#each pagesToShow as pageNumber}
					<Button on:click={() => goToPage(pageNumber)}>{pageNumber}</Button>
				{/each}
				<Button on:click={loadNextPage} disabled={totalPages === endPage}
					><ChevronRightOutline size="xs" class="m-1.5" /></Button
				>
			</ButtonGroup>
		</div>
	</TableSearch>
</Section>

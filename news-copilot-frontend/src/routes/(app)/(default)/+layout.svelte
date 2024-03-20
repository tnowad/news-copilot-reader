<script lang="ts">
	import {
		Navbar,
		NavBrand,
		NavLi,
		NavUl,
		NavHamburger,
		Avatar,
		Dropdown,
		DropdownItem,
		DropdownHeader,
		DropdownDivider,
		Input,
		Button,
		DarkMode
	} from 'flowbite-svelte';
	import { SearchOutline, ChevronDownOutline } from 'flowbite-svelte-icons';

	import {
		Footer,
		FooterCopyright,
		FooterLinkGroup,
		FooterBrand,
		FooterLink
	} from 'flowbite-svelte';
	import type { LayoutData } from './$types';

	const categoriesItems = [
		{ id: 1, label: 'Business', slug: 'business' },
		{ id: 2, label: 'Entertainment', slug: 'entertainment' },
		{ id: 3, label: 'General', slug: 'general' },
		{ id: 4, label: 'Health', slug: 'health' },
		{ id: 5, label: 'Science', slug: 'science' },
		{ id: 6, label: 'Sports', slug: 'sports' },
		{ id: 7, label: 'Technology', slug: 'technology' }
	];

	export let data: LayoutData;
</script>

<div class="flex min-h-screen flex-col">
	<Navbar>
		<NavBrand href="/">
			<img src="/images/logo.png" class="me-3 h-6 sm:h-9" alt="News Copilot Logo" />
			<span
				class="hidden self-center whitespace-nowrap text-xl font-semibold dark:text-white sm:block"
				>News Copilot</span
			>
		</NavBrand>

		<div class="flex items-center gap-x-5 md:order-2">
			<!-- Search component -->
			<Button
				color="none"
				data-collapse-toggle="mobile-menu-3"
				aria-controls="mobile-menu-3"
				aria-expanded="false"
				class="me-1 rounded-lg p-2.5 text-sm text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-4 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-700 lg:hidden"
			>
				<SearchOutline class="h-5 w-5" />
			</Button>
			<div class="relative hidden lg:block">
				<div class="pointer-events-none absolute inset-y-0 start-0 flex items-center ps-3">
					<SearchOutline class="h-4 w-4" />
				</div>
				<Input id="search-navbar" class="ps-10" placeholder="Search..." />
			</div>

			<DarkMode class="border text-primary-500 dark:border-gray-800 dark:text-primary-600" />

			{#if data.user}
				<Avatar id="avatar-menu" src="/images/default-profile-picture.png" />
			{:else}
				<Button href="/sign-in" size="sm">Get started</Button>
			{/if}

			<!-- Hamburger component -->
			<NavHamburger class1="w-full md:flex md:w-auto md:order-1" />
		</div>

		{#if data.user}
			<Dropdown placement="bottom" triggeredBy="#avatar-menu">
				<DropdownHeader>
					<span class="block text-sm">Welcome, {data.user.displayName}!</span>
					<span class="block truncate text-sm font-medium">{data.user.email}</span>
				</DropdownHeader>
				{#if data.user.roles?.some((role) => role === 'ADMIN')}
					<DropdownItem href="/admin">Admin Dashboard</DropdownItem>
				{/if}
				{#if data.user.roles?.some((role) => role === 'WRITER')}
					<a href="/admin"><DropdownItem href="/writer">Writer Dashboard</DropdownItem></a>
				{/if}
				{#if data.user.roles?.some((role) => role === 'USER')}
					<a href="/settings"><DropdownItem>Settings</DropdownItem></a>
					<a href="/bookmark"><DropdownItem>Bookmark</DropdownItem></a>
				{/if}
				<DropdownDivider />
				<DropdownItem href="/sign-out">Sign out</DropdownItem>
			</Dropdown>
		{/if}

		<NavUl>
			<NavLi href="/" active={true}>Latest News</NavLi>

			<NavLi class="cursor-pointer">
				Categories<ChevronDownOutline
					class="ms-2 inline h-3 w-3 text-primary-800 dark:text-white"
				/>
			</NavLi>
			<Dropdown>
				{#each categoriesItems as item}
					<DropdownItem href={`/categories/${item.slug}`}>{item.label}</DropdownItem>
				{/each}
			</Dropdown>

			<NavLi href="/about-us">About Us</NavLi>
		</NavUl>
	</Navbar>

	<main class="flex-1">
		<slot />
	</main>

	<Footer footerType="logo">
		<div class="container mx-auto">
			<div class="sm:flex sm:items-center sm:justify-between">
				<FooterBrand href="/" src="/images/logo.png" alt="News Copilot Logo" name="News Copilot" />
				<FooterLinkGroup
					ulClass="flex flex-wrap items-center mb-6 text-sm text-gray-500 sm:mb-0 dark:text-gray-400"
				>
					<FooterLink href="/about-us">About Us</FooterLink>
					<FooterLink href="/privacy">Privacy Policy</FooterLink>
					<FooterLink href="/License">Licensing</FooterLink>
					<FooterLink href="/contact">Contact</FooterLink>
				</FooterLinkGroup>
			</div>
		</div>
		<hr class="my-6 border-gray-200 dark:border-gray-700 sm:mx-auto lg:my-8" />
		<FooterCopyright href="/" by="News Copilot™" />
	</Footer>
</div>

<script lang="ts">
	import {
		Navbar,
		NavBrand,
		NavLi,
		NavUl,
		NavHamburger,
		Dropdown,
		DropdownItem,
		Button,
		DarkMode
	} from 'flowbite-svelte';
	import { ChevronDownOutline } from 'flowbite-svelte-icons';

	import {
		Footer,
		FooterCopyright,
		FooterLinkGroup,
		FooterBrand,
		FooterLink
	} from 'flowbite-svelte';
	import type { LayoutData } from './$types';
	import SearchInput from '$lib/widgets/search-input.svelte';
	import UserMenu from '$lib/widgets/user-menu.svelte';

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
			<SearchInput />
			<DarkMode class="border text-primary-500 dark:border-gray-800 dark:text-primary-600" />

			{#if data.user}
				<UserMenu user={data.user} />
			{:else}
				<Button href="/sign-in" size="sm">Get started</Button>
			{/if}

			<!-- Hamburger component -->
			<NavHamburger class1="w-full md:flex md:w-auto md:order-1" />
		</div>

		<NavUl>
			<NavLi href="/" active={true}>Latest News</NavLi>

			<NavLi class="cursor-pointer">
				Categories<ChevronDownOutline
					class="ms-2 inline h-3 w-3 text-primary-800 dark:text-white"
				/>
			</NavLi>
			<Dropdown>
				{#each data.categoryItems as category}
					<DropdownItem href={`/categories/${category.slug}/${category.id}`}
						>{category.title}</DropdownItem
					>
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
					<FooterLink href="/license">Licensing</FooterLink>
					<FooterLink href="/contact">Contact</FooterLink>
				</FooterLinkGroup>
			</div>
		</div>
		<hr class="my-6 border-gray-200 dark:border-gray-700 sm:mx-auto lg:my-8" />
		<FooterCopyright href="/" by="News Copilot™" />
	</Footer>
</div>

<script>
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
		Button
	} from 'flowbite-svelte';
	import { SearchOutline, ChevronDownOutline } from 'flowbite-svelte-icons';

	import {
		Footer,
		FooterCopyright,
		FooterLinkGroup,
		FooterBrand,
		FooterLink
	} from 'flowbite-svelte';

	const categoriesItems = [
		{ id: 1, label: 'Business', slug: 'business' },
		{ id: 2, label: 'Entertainment', slug: 'entertainment' },
		{ id: 3, label: 'General', slug: 'general' },
		{ id: 4, label: 'Health', slug: 'health' },
		{ id: 5, label: 'Science', slug: 'science' },
		{ id: 6, label: 'Sports', slug: 'sports' },
		{ id: 7, label: 'Technology', slug: 'technology' }
	];
</script>

<div class="flex flex-col min-h-screen">
	<Navbar>
		<NavBrand href="/">
			<img src="/images/logo.png" class="me-3 h-6 sm:h-9" alt="News Copilot Logo" />
			<span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white"
				>News Copilot</span
			>
		</NavBrand>
		<div class="flex items-center md:order-2 gap-x-5">
			<!-- Search component -->
			<Button
				color="none"
				data-collapse-toggle="mobile-menu-3"
				aria-controls="mobile-menu-3"
				aria-expanded="false"
				class="lg:hidden text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 rounded-lg text-sm p-2.5 me-1"
			>
				<SearchOutline class="w-5 h-5" />
			</Button>
			<div class="hidden relative lg:block">
				<div class="flex absolute inset-y-0 start-0 items-center ps-3 pointer-events-none">
					<SearchOutline class="w-4 h-4" />
				</div>
				<Input id="search-navbar" class="ps-10" placeholder="Search..." />
			</div>

			<!-- Avatar component -->
			<Avatar id="avatar-menu" src="/images/default-profile-picture.png" />

			<!-- Hamburger component -->
			<NavHamburger class1="w-full md:flex md:w-auto md:order-1" />
		</div>
		<Dropdown placement="bottom" triggeredBy="#avatar-menu">
			<DropdownHeader>
				<span class="block text-sm">Welcome Display Name!</span>
				<span class="block truncate text-sm font-medium">name@email.com</span>
			</DropdownHeader>
			<DropdownItem>Dashboard</DropdownItem>
			<DropdownItem>Settings</DropdownItem>
			<DropdownItem>Bookmark</DropdownItem>
			<DropdownDivider />
			<DropdownItem>Sign out</DropdownItem>
		</Dropdown>

		<NavUl>
			<NavLi href="/" active={true}>Latest News</NavLi>

			<NavLi class="cursor-pointer">
				Categories<ChevronDownOutline
					class="w-3 h-3 ms-2 text-primary-800 dark:text-white inline"
				/>
			</NavLi>
			<Dropdown>
				{#each categoriesItems as item}
					<DropdownItem href={`/categories/${item.slug}/${item.id}`}>{item.label}</DropdownItem>
				{/each}
			</Dropdown>

			<NavLi href="/about-us">About Us</NavLi>
		</NavUl>
	</Navbar>

	<main class="flex-1">
		<slot />
	</main>

	<Footer footerType="logo">
		<div class="mx-auto container">
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
		<hr class="my-6 border-gray-200 sm:mx-auto dark:border-gray-700 lg:my-8" />
		<FooterCopyright href="/" by="News Copilot™" />
	</Footer>
</div>

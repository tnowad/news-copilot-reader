<script lang="ts">
	import { page } from '$app/stores';
	import { afterNavigate } from '$app/navigation';
	import {
		Sidebar,
		SidebarGroup,
		SidebarItem,
		SidebarWrapper,
		SidebarDropdownWrapper,
		DarkMode,
		NavBrand,
		NavHamburger,
		Navbar
	} from 'flowbite-svelte';
	import { ClipboardListSolid, ListSolid } from 'flowbite-svelte-icons';
	import {
		AngleDownSolid,
		AngleUpOutline,
		PieChartSolid,
		TableColumnSolid
	} from 'flowbite-svelte-icons';
	import UserMenu from '$lib/widgets/user-menu.svelte';
	import type { LayoutData } from './$types';
	import UserSidebar from '$lib/widgets/user-sidebar.svelte';
	let drawerHidden = false;

	const closeDrawer = () => {
		drawerHidden = true;
	};

	let iconClass =
		'flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white';
	let itemClass =
		'flex items-center p-2 text-base text-gray-900 transition duration-75 rounded-lg hover:bg-gray-100 group dark:text-gray-200 dark:hover:bg-gray-700';
	let groupClass = 'pt-2 space-y-2';

	$: mainSidebarUrl = $page.url.pathname;
	let activeMainSidebar: string;

	afterNavigate((navigation) => {
		document.getElementById('svelte')?.scrollTo({ top: 0 });
		closeDrawer();

		activeMainSidebar = navigation.to?.url.pathname ?? '';
	});

	let menuItems = [
		{ name: 'Dashboard', icon: PieChartSolid, href: '/dashboard' },
		{
			name: 'Articles',
			icon: TableColumnSolid,
			children: {
				'Manage Articles': '/writer/article',
				Categories: '/writer/catagories'
			}
		}
	];

	let dropdowns = Object.fromEntries(Object.keys(menuItems).map((x) => [x, false]));
	export let data: LayoutData;
</script>

<div class="flex min-h-screen flex-col">
	<header
		class="sticky top-0 z-40 mx-auto w-full flex-none border-b border-gray-200 bg-white dark:border-gray-600 dark:bg-gray-800"
	>
		<Navbar fluid={true} class="text-black" color="default" let:NavContainer>
			<NavContainer fluid={true} class="mb-px mt-px px-1">
				<NavHamburger
					onClick={() => (drawerHidden = !drawerHidden)}
					class="m-0 me-3 md:block lg:hidden"
				/>
				<NavBrand href="/" class="lg:w-60">
					<img src="/images/logo.png" class="me-2.5 h-6 sm:h-8" alt="News Copilot Logo" />
					<span
						class="ml-px self-center whitespace-nowrap text-xl font-semibold dark:text-white sm:text-2xl"
					>
						News Copilot
					</span>
				</NavBrand>
				<div class="ms-auto flex items-center gap-x-5 text-gray-500 dark:text-gray-400 sm:order-2">
					<!-- <Notifications /> -->
					<!-- <AppsMenu /> -->
					<DarkMode />
					<UserMenu user={data.user} />
				</div>
			</NavContainer>
		</Navbar>
	</header>

	<div class="flex-1 overflow-hidden lg:flex">
		<Sidebar
			class={drawerHidden ? 'hidden' : ''}
			activeUrl={mainSidebarUrl}
			activeClass="bg-gray-100 dark:bg-gray-700"
			asideClass="fixed inset-0 z-30 flex-none h-full w-64 lg:h-auto border-e border-gray-200 dark:border-gray-600 lg:overflow-y-visible lg:pt-16 lg:block"
		>
			<h4 class="sr-only">Main menu</h4>
			<SidebarWrapper
				divClass="overflow-y-auto px-3 pt-20 lg:pt-5 h-full bg-white scrolling-touch max-w-2xs lg:h-[calc(100vh-4rem)] lg:block dark:bg-gray-800 lg:me-0 lg:sticky top-2"
			>
				<nav class="divide-y divide-gray-200 dark:divide-gray-700">
					<SidebarGroup ulClass={groupClass} class="mb-3">
						{#each menuItems as { name, icon, children, href } (name)}
							{#if children}
								<SidebarDropdownWrapper bind:isOpen={dropdowns[name]} label={name} class="pr-3">
									<AngleDownSolid slot="arrowdown" strokeWidth="3.3" size="sm" />
									<AngleUpOutline slot="arrowup" strokeWidth="3.3" size="sm" />
									<svelte:component this={icon} slot="icon" class={iconClass} />

									{#each Object.entries(children) as [title, href]}
										<SidebarItem
											label={title}
											{href}
											spanClass="ml-9"
											class={itemClass}
											active={activeMainSidebar === href}
										>
											<!--<svelte:component this={childIcon} slot="icon" class={iconClass} />-->
										</SidebarItem>
									{/each}
								</SidebarDropdownWrapper>
							{:else}
								<SidebarItem
									label={name}
									{href}
									spanClass="ml-3"
									class={itemClass}
									active={activeMainSidebar === href}
								>
									<svelte:component this={icon} slot="icon" class={iconClass} />
								</SidebarItem>
							{/if}
						{/each}
					</SidebarGroup>
				</nav>
			</SidebarWrapper>
		</Sidebar>

		<div class="relative h-full w-full overflow-y-auto lg:ml-64">
			<slot />
		</div>
	</div>

	<div
		hidden={drawerHidden}
		class="fixed inset-0 z-20 bg-gray-900/50 dark:bg-gray-900/60"
		on:click={closeDrawer}
		on:keydown={closeDrawer}
		role="presentation"
	/>
	<!-- <UserSidebar/>-->
</div>

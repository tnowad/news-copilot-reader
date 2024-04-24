<script lang="ts">
	import { page } from '$app/stores';
	import { afterNavigate } from '$app/navigation';
	import {
		Sidebar,
		SidebarGroup,
		SidebarItem,
		SidebarWrapper,
		SidebarDropdownWrapper,
		Avatar,
		Heading
	} from 'flowbite-svelte';
	import {
		BookOpenSolid,
		FlagSolid,
		MessageCaptionSolid,
		UserCircleSolid
	} from 'flowbite-svelte-icons';
	import {
		AngleDownSolid,
		AngleUpOutline,
		PieChartSolid,
		TableColumnSolid
	} from 'flowbite-svelte-icons';
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
		{
			name: 'Profile',
			icon: TableColumnSolid,
			href: '/profile/'
		},
		{
			name: 'Chat',
			icon: BookOpenSolid,
			href: '/chat'
		},
		{
			name: 'Bookmarks',
			icon: MessageCaptionSolid,
			href: '/bookmarks'
		}
	];

	let dropdowns = Object.fromEntries(Object.keys(menuItems).map((x) => [x, false]));
	export let data;
</script>

<div class="container mx-0 mx-auto flex w-full space-x-4">
	<Sidebar
		class={drawerHidden ? 'hidden' : ''}
		activeUrl={mainSidebarUrl}
		activeClass="bg-gray-100 dark:bg-gray-700"
		asideClass="bg-gray-800 z-30 flex-none w-64 border border-gray-200 dark:border-gray-600 lg:overflow-y-visible lg:block"
	>
		<h4 class="sr-only">Main menu</h4>
		<SidebarWrapper
			divClass="overflow-y-auto px-3 pt-10 bg-white scrolling-touch max-w-2xs lg:block dark:bg-gray-800 lg:me-0 lg:sticky top-2"
		>
			<nav class="divide-y divide-gray-200 dark:divide-gray-700">
				<SidebarGroup ulClass={groupClass} class="mb-3">
					<div class="flex w-full space-x-2">
						<Avatar
							class="2xl:mb-0 mb-4 h-20 w-20 overflow-hidden rounded-lg sm:mb-0 xl:mb-4"
							size="none"
							rounded
						>
							<img src={data.user?.avatarImage} class="h-full w-full object-cover" alt="Avatar" />
						</Avatar>

						<div class="py-0.5">
							<p class="text-gray-600 dark:text-gray-400">{data.user?.email}</p>
							<p class="text-gray-600 dark:text-gray-400">{data.user?.displayName}</p>
						</div>
					</div>
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

	<slot />
</div>

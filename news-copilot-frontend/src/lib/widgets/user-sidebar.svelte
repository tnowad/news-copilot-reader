<script>
    import { page } from '$app/stores';
    import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper } from 'flowbite-svelte';
    import { ChartSolid, GridSolid, MailBoxSolid, UserSolid, ArrowRightToBracketSolid } from 'flowbite-svelte-icons';
    $: activeUrl = $page.url.pathname;
  </script>
  
  <Sidebar {activeUrl}>
    <SidebarWrapper>
      <SidebarGroup>
        <SidebarItem label="Dashboard" href="/">
          <svelte:fragment slot="icon">
            <ChartSolid class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
          </svelte:fragment>
        </SidebarItem>
        <SidebarItem label="Accordion" href="/docs/components/accordion">
          <svelte:fragment slot="icon">
            <GridSolid class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
          </svelte:fragment>
        </SidebarItem>
        <SidebarItem label="Alert" href="/docs/components/alert">
          <svelte:fragment slot="icon">
            <MailBoxSolid class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
          </svelte:fragment>
        </SidebarItem>
        <SidebarItem label="Sidebar" href="/docs/components/sidebar">
          <svelte:fragment slot="icon">
            <UserSolid class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
          </svelte:fragment>
        </SidebarItem>
        <SidebarItem label="Badge" href="/docs/components/badge">
          <svelte:fragment slot="icon">
            <ArrowRightToBracketSolid class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
          </svelte:fragment>
        </SidebarItem>
      </SidebarGroup>
    </SidebarWrapper>
  </Sidebar>
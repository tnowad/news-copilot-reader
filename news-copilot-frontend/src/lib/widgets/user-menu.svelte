<script lang="ts">
	import { Avatar, Dropdown, DropdownItem, DropdownHeader, DropdownDivider } from 'flowbite-svelte';
	import type { User } from '$lib/services/types';

	export let user: User;
</script>

<Avatar id="avatar-menu" src={user.avatarImage ?? '/images/default-profile-picture.png'} />

<Dropdown placement="bottom" triggeredBy="#avatar-menu">
	<DropdownHeader>
		<span class="block text-sm">Welcome, {user.displayName}!</span>
		<span class="block truncate text-sm font-medium">{user.email}</span>
	</DropdownHeader>
	{#if user.roles?.some((role) => role === 'ADMIN')}
		<DropdownItem href="/dashboard">Admin Dashboard</DropdownItem>
	{/if}
	{#if user.roles?.some((role) => role === 'WRITER')}
		<DropdownItem href="/dashboard">Writer Dashboard</DropdownItem>
	{/if}
	<DropdownItem href="/profile">Profile</DropdownItem>

	{#if user.roles?.some((role) => role === 'USER')}
		<DropdownItem href="/settings">Settings</DropdownItem>
		<DropdownItem href="/bookmark">Bookmark</DropdownItem>
	{/if}
	<DropdownDivider />
	<DropdownItem href="/sign-out">Sign out</DropdownItem>
</Dropdown>

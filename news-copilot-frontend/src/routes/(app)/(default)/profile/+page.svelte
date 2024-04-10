<script lang="ts">
	import {
		Card,
		Heading,
		Breadcrumb,
		BreadcrumbItem,
		Avatar,
		Button,
		Input,
		Label,
		Badge,
		Textarea
	} from 'flowbite-svelte';
	import { UploadSolid } from 'flowbite-svelte-icons';
	import type { PageData } from './$types';
	import { enhance } from '$app/forms';
	import { onMount } from 'svelte';

	export let data: PageData;

	let avatarInputElement: HTMLInputElement | null = null;
	let avatarImageSrc = data.user?.avatarImage ?? '/images/default-profile-picture.png';

	onMount(() => {
		if (avatarInputElement) {
			avatarInputElement.onchange = () => {
				if (avatarInputElement == null) {
					return;
				}

				if (!avatarInputElement.files?.length) {
					return;
				}

				if (avatarInputElement.files.length > 0) {
					const file = avatarInputElement.files[0];
					avatarImageSrc = URL.createObjectURL(file);
				}
			};
		}
	});
</script>

<section>
	<div class="container mx-auto">
		<div class="col-span-full mt-6 xl:mb-0">
			<Breadcrumb class="mb-6">
				<BreadcrumbItem home>Home</BreadcrumbItem>
				<BreadcrumbItem
					class="inline-flex items-center text-gray-700 hover:text-primary-600 dark:text-gray-300 dark:hover:text-white"
					href="/curd/users">Users</BreadcrumbItem
				>
				<BreadcrumbItem>Settings</BreadcrumbItem>
			</Breadcrumb>

			<Heading tag="h1" class="text-xl font-semibold text-gray-900 dark:text-white sm:text-2xl">
				User settings
			</Heading>
		</div>

		<div class="grid grid-cols-1 gap-2 xl:grid-cols-12 xl:gap-3.5">
			<Card
				size="none"
				class="2xl:flex 2xl:space-x-4 block shadow-sm sm:flex sm:space-x-4 sm:py-6 xl:col-span-4 xl:block xl:space-x-0"
				horizontal
			>
				<Avatar
					class="2xl:mb-0 mb-4 h-28 w-28 overflow-hidden rounded-lg sm:mb-0 xl:mb-4"
					size="none"
					rounded
				>
					<img src={avatarImageSrc} class="h-full w-full object-cover" alt="Avatar" />
				</Avatar>

				<div class="py-0.5">
					<Heading tag="h3" class="text-xl">Profile picture</Heading>
					<p class="mb-4 mt-1 pt-px text-sm">JPG, GIF or PNG. Max size of 800K</p>
					<div class="flex items-center space-x-4">
						<Button size="sm" class="px-3" on:click={() => avatarInputElement?.click()}
							><UploadSolid size="sm" class="-ms-1 me-2" /> Upload picture</Button
						>
					</div>
				</div>
			</Card>
			<Card class="xl:col-span-8" size="none">
				<Heading tag="h3" class="text-xl">General Information</Heading>
				<form
					class="grid grid-cols-6 gap-6"
					action="/profile"
					method="post"
					use:enhance
					enctype="multipart/form-data"
				>
					<Label class="col-span-6 space-y-2 sm:col-span-3">
						<span>Display Name:</span>
						<Input
							type="text"
							class="border font-normal outline-none"
							name="displayName"
							value={data.user?.displayName}
						/>
					</Label>

					<Label class="col-span-6 space-y-2 sm:col-span-3">
						<span>Phone number:</span>
						<Input
							type="text"
							value={data.user?.phoneNumber}
							name="phoneNumber"
							class="border font-normal outline-none"
						/>
					</Label>

					<Label class="col-span-6 space-y-2 sm:col-span-3">
						<span>Email address:</span>
						<Input
							type="text"
							class="border font-normal outline-none"
							value={data.user?.email}
							name="email"
							disabled
						/>
					</Label>

					<Label class="col-span-6 space-y-2 sm:col-span-3">
						<span>Birthday:</span>
						<Input
							type="date"
							value={data.user?.birthDate}
							name="birthDate"
							class="border font-normal outline-none"
						/>
					</Label>

					<Label class="col-span-6 space-y-2 sm:col-span-3">
						<span>Password:</span>
						<Input
							type="password"
							placeholder="••••••••"
							name="password"
							class="border font-normal outline-none"
							required
						/>
					</Label>

					<Label class="col-span-6 space-y-2 sm:col-span-3">
						<span>New Password:</span>
						<Input
							type="password"
							name="newPassword"
							placeholder="••••••••"
							class="border font-normal outline-none"
						/>
					</Label>

					<Label class="col-span-full space-y-2">
						<span>Bio:</span>
						<Textarea
							value={data.user?.bio}
							name="bio"
							class="w-full border font-normal outline-none"
						/>
					</Label>

					<Label class="hidden">
						<span>Avatar Image</span>
						<input bind:this={avatarInputElement} type="file" name="avatarImage" />
					</Label>
					<Label class="col-span-full space-y-2">
						<span>Role:</span>
						<div class="flex gap-x-2">
							{#each data.user?.roles ?? [] as role}
								<Badge>{role}</Badge>
							{/each}
						</div>
					</Label>

					<Button type="submit" class="w-fit whitespace-nowrap">Save all</Button>
				</form>
			</Card>
		</div>
	</div>
</section>

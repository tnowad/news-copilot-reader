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
		Textarea,
		Fileupload
	} from 'flowbite-svelte';
	import type { PageData } from './$types';
	import { enhance } from '$app/forms';

	export let data: PageData;
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
					<img src={data.user?.avatarImage} class="h-full w-full object-cover" alt="Avatar" />
				</Avatar>

				<div class="py-0.5">
					<Heading tag="h3" class="text-xl">Profile information</Heading>
					<p class="text-gray-600 dark:text-gray-400">{data.user?.email}</p>
					<p class="text-gray-600 dark:text-gray-400">{data.user?.phoneNumber}</p>
					<p class="text-gray-600 dark:text-gray-400">{data.user?.displayName}</p>
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
						<span>Avatar Image:</span>
						<Fileupload name="avatarImage" class="border font-normal outline-none" />
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

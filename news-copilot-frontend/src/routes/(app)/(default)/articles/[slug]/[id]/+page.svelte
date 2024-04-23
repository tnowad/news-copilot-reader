<script lang="ts">
	import type { ActionData, PageData } from './$types';
	import { Modal } from 'flowbite-svelte';
	import Markdown from '$lib/widgets/markdown.svelte';
	import ArticleSection from '$lib/widgets/article-section.svelte';
	import { Avatar } from 'flowbite-svelte';
	import {
		Toolbar,
		ToolbarButton,
		Textarea,
		Button,
		Breadcrumb,
		BreadcrumbItem,
		Img,
		Card,
		Heading,
		Dropdown,
		Label,
		Input,
		Select,
		DropdownItem,
		Badge
	} from 'flowbite-svelte';
	import {
		PaperClipOutline,
		MapPinAltSolid,
		ImageOutline,
		DotsHorizontalOutline
	} from 'flowbite-svelte-icons';
	import { CommentItem, Section } from 'flowbite-svelte-blocks';
	import { onMount } from 'svelte';
	import { enhance } from '$app/forms';
	import { StatusCodes } from 'http-status-codes';
	import { toasts } from 'svelte-toasts';

	let commentEditingId: number | null;
	let commentDeleteId: number | null;
	let defaultModal = false;
	let articleReportModal = false;
	let userReportModal = false;
	export let data: PageData;
	export let form: ActionData;

	const markArticleViewed = async () => {
		if (!data.article?.id) {
			return;
		}

		const formData = new FormData();
		formData.append('articleId', data.article.id as unknown as string);

		fetch(`/articles/${data.article?.slug}/${data.article?.id}?/markViewed`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: formData
		});
	};
	$: {
		if (form) {
			if (form.statusCode >= 200 && form.statusCode < 300) {
				toasts.success(form.message);
			} else {
				toasts.error(form.message);
			}
		}
	}
	onMount(() => {
		markArticleViewed();
	});
</script>

<section>
	<div class="container mx-auto">
		<div class="col-span-full mt-6 xl:mb-0">
			<Breadcrumb class="mb-6">
				<BreadcrumbItem home href="/">Home</BreadcrumbItem>
				<BreadcrumbItem
					class="inline-flex items-center text-gray-700 hover:text-primary-600 dark:text-gray-300 dark:hover:text-white"
					href="/articles">Article</BreadcrumbItem
				>
				<BreadcrumbItem>{data.article?.title}</BreadcrumbItem>
			</Breadcrumb>
		</div>
	</div>
</section>

<section>
	<div class="container mx-auto">
		<Card size="none" shadow={false}>
			<Heading class="text-center">{data.article?.title}</Heading>

			{#if data.article?.createdAt}
				<div class="mt-2 flex justify-center">
					<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
						{new Date(data.article?.createdAt).toLocaleDateString()}
					</p>
				</div>
			{/if}

			{#if data.article?.categories}
				<div class="mt-2 flex flex-wrap justify-center gap-1">
					{#each data.article?.categories as category}
						<Badge>{category.title.toUpperCase()}</Badge>
					{/each}
				</div>
			{/if}

			{#if data.article?.coverImage}
				<div class="my-6 flex justify-center">
					<Img src={data.article?.coverImage} alt={data.article?.title} imgClass="rounded-md" />
				</div>
			{/if}

			{#if data.article?.summary}
				<div class="mt-2">
					<span class="font-bold">Summary: </span>
					<span class="text-sm font-medium">
						{data.article?.summary}
					</span>
				</div>
			{/if}

			<div>
				<Markdown source={data.article?.content} />
			</div>

			<div class="m-3 flex items-center justify-between">
				<a href={`/users/${data.article?.author?.id}`}>
					<div class="flex space-x-4 rtl:space-x-reverse">
						<Avatar
							class="h-10 w-10"
							src={data.article?.author?.avatarImage}
							alt={data.article?.author?.displayName}
						/>
						<div class="flex flex-col">
							<h4 class="text-sm font-bold dark:text-white">
								{data.article?.author?.displayName}
							</h4>
							{#if data.article?.createdAt}
								<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
									{new Date(data.article?.createdAt).toLocaleDateString()}
								</p>
							{/if}
						</div>
					</div>
				</a>
				<div class="mt-3 text-center">
					{#if data.bookmark}
						<form
							action={`/articles/${data.article?.slug}/${data.article?.id}?/deleteBookmark`}
							method="post"
							use:enhance
						>
							<input type="hidden" name="bookmarkId" value={data.bookmark.id} />

							<Button type="submit">Unbookmark</Button>
						</form>
					{:else}
						<form
							action={`/articles/${data.article?.slug}/${data.article?.id}?/createBookmark`}
							method="post"
							use:enhance
						>
							<input type="hidden" name="articleId" value={data.article?.id} />

							<Button type="submit">Bookmark</Button>
						</form>
					{/if}
				</div>
				<div class="m-5 flex justify-center">
					<Button on:click={() => (articleReportModal = true)}>Report</Button>
				</div>
				<Modal
					title="Reporting an article"
					bind:open={articleReportModal}
					autoclose={false}
					class="min-w-full"
				>
					<form
						action={`/articles/${data.article?.slug}/${data.article?.id}?/createArticleReport`}
						method="post"
					>
						<Label class="mb-2">Description</Label>
						<Textarea
							id="description"
							placeholder="Your description here"
							rows="4"
							name="reportArticleContent"
							required
						/>
						<Button type="submit" class="w-52">Report</Button>
					</form>
				</Modal>
			</div>
		</Card>

		<ArticleSection title="Recommend for you" articles={data.recommendArticles} />
		<Section name="comment" sectionClass="mt-5" classDiv="max-w-none w-full px-0">
			<form
				action={`/articles/${data.article?.slug}/${data.article?.id}?/createComment`}
				method="post"
				use:enhance
			>
				<Textarea class="mb-4" placeholder="Write a comment" name="content">
					<div slot="footer" class="flex items-center justify-between">
						<Button type="submit">Post comment</Button>
					</div>
				</Textarea>
			</form>
			<p class="mb-6 ms-auto text-xs text-gray-500 dark:text-gray-400">
				Remember, contributions to this article should follow our
				<a href="/" class="text-blue-600 hover:underline dark:text-blue-500">
					Community Guidelines
				</a>
				.
			</p>

			{#each data.comments as comment, i}
				<CommentItem
					comment={{
						id: comment.id + '',
						commenter: {
							name:
								(comment.author?.displayName || 'unknown') +
								(data.article?.author?.id === comment.author?.id ? ' (Author)' : ''),
							profilePicture: comment.author?.avatarImage
						},
						content: comment.content,
						date: comment.createdAt
					}}
					articleClass={i !== 0 ? 'border-t border-gray-200 dark:border-gray-700 rounded-none' : ''}
				>
					<svelte:fragment slot="dropdownMenu">
						<DotsHorizontalOutline
							id={`dots-menu-${comment.id}`}
							class="dots-menu dark:text-white"
						/>
						<Dropdown triggeredBy={`#dots-menu-${comment.id}`}>
							{#if data.user?.id == comment.author?.id}
								<DropdownItem
									on:click={() => {
										commentEditingId = comment.id;
									}}>Edit</DropdownItem
								>
							{/if}
							{#if data.user?.id == comment.author?.id || data.user?.roles?.includes('ADMIN')}
								<DropdownItem
									on:click={() => {
										commentDeleteId = comment.id;
										defaultModal = true;
									}}>Remove</DropdownItem
								>
							{/if}
							<DropdownItem
								on:click={() => {
									userReportModal = true;
								}}>Report</DropdownItem
							>
							<Modal
								title="Reporting a comment"
								bind:open={userReportModal}
								autoclose={false}
								class="min-w-full"
							>
								<form
									action={`/articles/${data.article?.slug}/${data.article?.id}?/createCommentReport`}
									method="post"
								>
									<Label class="mb-2">Description</Label>
									<Textarea
										id="description"
										placeholder="Your description here"
										rows="4"
										name="reportCommentContent"
										required
									/>
									<input type="hidden" name="reportCommentId" value={comment.id} />
									<Button type="submit" class="w-52">Report</Button>
								</form>
							</Modal>
						</Dropdown>
					</svelte:fragment>
					<svelte:fragment slot="reply">
						{#if comment.id == commentEditingId}
							<form
								class="mt-3"
								action={`/articles/${data.article?.slug}/${data.article?.id}?/updateComment`}
								method="post"
								use:enhance={() => {
									commentEditingId = null;
								}}
							>
								<input type="hidden" name="commentId" value={comment.id} />
								<Textarea
									class="mb-4"
									placeholder="Write a comment"
									name="content"
									value={comment.content}
								>
									<div slot="footer" class="flex items-center justify-between">
										<Button type="submit">Post comment</Button>
										<Toolbar embedded>
											<ToolbarButton name="Attach file"
												><PaperClipOutline class="h-5 w-5 rotate-45" /></ToolbarButton
											>
											<ToolbarButton name="Embed map"
												><MapPinAltSolid class="h-5 w-5" /></ToolbarButton
											>
											<ToolbarButton name="Upload image"
												><ImageOutline class="h-5 w-5" /></ToolbarButton
											>
										</Toolbar>
									</div>
								</Textarea>
							</form>
						{/if}

						{#if comment.id == commentDeleteId}
							<form
								action={`/articles/${data.article?.slug}/${data.article?.id}?/deleteComment`}
								method="post"
								use:enhance={() => {
									commentDeleteId = null;
								}}
							>
								<Modal title="Delete Comment" bind:open={defaultModal}>
									<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
										Do you want to delete this comment?
									</p>
									<input type="hidden" name="commentId" value={comment.id} />
									<svelte:fragment slot="footer">
										<Button type="submit">Yes</Button>
										<Button
											on:click={() => {
												commentDeleteId = null;
												defaultModal = false;
											}}
											color="alternative">No</Button
										>
									</svelte:fragment>
								</Modal>
							</form>
						{/if}
					</svelte:fragment>
				</CommentItem>
			{/each}
		</Section>
	</div>
</section>

<script lang="ts">
	import type { PageData } from './$types';
	import { Modal } from 'flowbite-svelte';
	import Markdown from '$lib/widgets/markdown.svelte';
	import ArticleSection from '$lib/widgets/article-section.svelte';
	import { Avatar, DropdownHeader, DropdownDivider, Tooltip } from 'flowbite-svelte';
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
		DropdownItem
	} from 'flowbite-svelte';
	import {
		PaperClipOutline,
		MapPinAltSolid,
		ImageOutline,
		DotsHorizontalOutline
	} from 'flowbite-svelte-icons';
	import { CommentItem, Section } from 'flowbite-svelte-blocks';
	import { onMount } from 'svelte';
	let comments = [];
	let commentContent = '';
	$: comments = data.comments;
	const postComment = () => {
		alert(commentContent);
	};

	let commentEditingId: data | null;
	let commentDeleteId: data | null;
	let defaultModal = false;

	export let data: PageData;

	const markArticleViewed = async () => {
		if (!data.article?.id) {
			return;
		}

		const formData = new FormData();
		formData.append('articleId', data.article.id);

		fetch(`/articles/${data.article?.slug}/${data.article?.id}?/markViewed`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: formData
		});
	};
	onMount(() => {
		markArticleViewed();
	});
</script>

<section>
	<div class="container">
		<div class="col-span-full mt-6 xl:mb-0">
			<Breadcrumb class="mb-6">
				<BreadcrumbItem href="../">Home</BreadcrumbItem>
				<BreadcrumbItem
					class="inline-flex items-center text-gray-700 hover:text-primary-600 dark:text-gray-300 dark:hover:text-white"
					href="/curd/users">Article</BreadcrumbItem
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
			<form
				action={`/articles/${data.article?.slug}/${data.article?.id}?/bookmarkArticle`}
				method="post"
			>
				<input type="hidden" name="category-id" value={data.article?.id} />
				<Button type="submit">Bookmark</Button>
			</form>
			<div>Author Image and name</div>
			<div>Summary</div>

			<div class="flex justify-center">
				<Img src={data.article?.coverImage} alt={data.article?.title} imgClass="rounded-md" />
			</div>
			<div>
				<Markdown source={data.article?.content} />
			</div>
		</Card>

		<a href={`/users/${data.article?.author.id}`}>
			<div class="mt-6 flex space-x-4 rtl:space-x-reverse">
				<Avatar
					class="h-10 w-10"
					src={data.article?.author.avatarImage}
					alt={data.article?.author.displayName}
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

		<ArticleSection title="Recommend for you" articles={data.recommendArticles} />
		<Section name="comment" sectionClass="mt-5" classDiv="max-w-none w-full px-0">
			<form
				action={`/articles/${data.article?.slug}/${data.article?.id}?/createComment`}
				method="post"
			>
				<Textarea
					class="mb-4"
					placeholder="Write a comment"
					name="content"
					bind:vaule={commentContent}
				>
					<div slot="footer" class="flex items-center justify-between">
						<Button type="submit">Post comment</Button>
						<Toolbar embedded>
							<ToolbarButton name="Attach file"
								><PaperClipOutline class="h-5 w-5 rotate-45" /></ToolbarButton
							>
							<ToolbarButton name="Embed map"><MapPinAltSolid class="h-5 w-5" /></ToolbarButton>
							<ToolbarButton name="Upload image"><ImageOutline class="h-5 w-5" /></ToolbarButton>
						</Toolbar>
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

			{#each comments as comment, i}
				{#key comment.id}
					<CommentItem
						comment={{
							id: comment.id,
							commenter: {
								name: comment.author.displayName,
								profilePicture: comment.author.avatarImage
							},
							content: comment.content,
							date: comment.date,
							replies: comment?.childComments?.map((childComment) => {
								return {
									id: childComment.id,
									commenter: {
										name: childComment.author.name,
										profilePicture: childComment.author.avatarImage
									},
									content: childComment.content,
									date: childComment.date
								};
							})
						}}
						articleClass={i !== 0
							? 'border-t border-gray-200 dark:border-gray-700 rounded-none'
							: ''}
					>
						<svelte:fragment slot="dropdownMenu">
							<DotsHorizontalOutline class="dots-menu dark:text-white" />
							<Dropdown triggeredBy=".dots-menu">
								{#if data.user?.id == comment.author.id}
									<DropdownItem
										on:click={() => {
											commentEditingId = comment.id;
										}}>Edit</DropdownItem
									>

									<DropdownItem
										on:click={() => {
											commentDeleteId = comment.id;
										}}>Remove</DropdownItem
									>
								{/if}
								<DropdownItem>Report</DropdownItem>
							</Dropdown>
						</svelte:fragment>
						<svelte:fragment slot="reply">
							{#if comment.id == commentEditingId}
								<form
									action={`/articles/${data.article?.slug}/${data.article?.id}?/updateComment`}
									method="post"
								>
									<Textarea
										class="mb-4"
										placeholder="Write a comment"
										name="content"
										value={comment.value}
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
									action={`/articles/${data.article?.slug}/${data.article?.id}?/updateComment`}
									method="post"
								>
									<Button on:click={() => (defaultModal = true)}>Remove comment ??</Button>
									<Modal title="Terms of Service" bind:open={defaultModal} autoclose>
										<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
											You can't unchange this action, if you agree click "I accept". If not, click
											"Decline"
										</p>
										<svelte:fragment slot="footer">
											<Button on:click={() => alert('Handle "success"')}>I accept</Button>
											<Button color="alternative">Decline</Button>
										</svelte:fragment>
									</Modal>
								</form>
							{/if}
						</svelte:fragment>
					</CommentItem>
				{/key}
			{/each}
		</Section>
	</div>
</section>

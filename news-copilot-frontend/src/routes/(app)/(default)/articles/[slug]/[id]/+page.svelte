<script lang="ts">
	import type { PageData } from './$types';
	import Markdown from '$lib/widgets/markdown.svelte';

	import {
		Toolbar,
		ToolbarButton,
		Textarea,
		Button,
		Card,
		Heading,
		Img,
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
	let comments = [];
	let commentContent = '';
	$: comments = data.comments;
	const postComment = () => {
		alert(commentContent);
	}
	export let data: PageData;
</script>

<section>
	<div class="container mx-auto">
		<Heading class="text-center">{data.article?.title}</Heading>

		<!-- <div class="flex justify-center"> -->
		<!-- 	<Img src={data.article?.coverImage} alt={data.article?.title} imgClass="rounded-md" /> -->
		<!-- </div> -->
		<Card size="none" shadow={false}>
			<Markdown source={data.article?.content} />
		</Card>

		<Section name="comment" sectionClass="mt-5" classDiv="max-w-none w-full px-0">
			<form  action={`/articles/${data.article?.slug}/${data.article?.id}`} method="post">
				<Textarea class="mb-4" placeholder="Write a comment" name="content" bind:vaule={commentContent}>
					<div slot="footer" class="flex items-center justify-between">
						<Button type="submit" >Post comment</Button>
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
			<p class="ms-auto text-xs text-gray-500 dark:text-gray-400">
				Remember, contributions to this article should follow our
				<a href="/" class="text-blue-600 hover:underline dark:text-blue-500">
					Community Guidelines
				</a>
				.
			</p>

			{#each comments as comment, i}
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
					}
					articleClass={i !== 0 ? 'border-t border-gray-200 dark:border-gray-700 rounded-none' : ''}
				>
					<svelte:fragment slot="dropdownMenu">
						<DotsHorizontalOutline class="dots-menu dark:text-white" />
						<Dropdown triggeredBy=".dots-menu">
							<DropdownItem>Edit</DropdownItem>
							<DropdownItem>Remove</DropdownItem>
							<DropdownItem>Report</DropdownItem>
						</Dropdown>
					</svelte:fragment>
				</CommentItem>
			{/each}
		</Section>
	</div>
</section>

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

	const comments = [
		{
			id: 'comment1',
			author: {
				name: 'Michael Gough',
				avatarImage: 'https://flowbite.com/docs/images/people/profile-picture-2.jpg'
			},
			date: 'Feb. 8, 2022',
			content:
				'Very straight-to-point article. Really worth time reading. Thank you! But tools are just the instruments for the UX designers. The knowledge of the design tools are as important as the creation of the design strategy.',
			childComments: [
				{
					id: 'reply1',
					author: {
						name: 'Jese Leos',
						avatarImage: 'https://flowbite.com/docs/images/people/profile-picture-5.jpg'
					},
					date: 'Feb. 12, 2022',
					content: 'Much appreciated! Glad you liked it ☺️'
				}
			]
		},
		{
			id: 'comment2',
			author: {
				name: 'Bonnie Green',
				avatarImage: 'https://flowbite.com/docs/images/people/profile-picture-3.jpg'
			},
			date: 'Mar. 12, 2022',
			content:
				'The article covers the essentials, challenges, myths and stages the UX designer should consider while creating the design strategy.',
			childComments: []
		},
		{
			id: 'comment3',
			author: {
				name: 'Helene Engels',
				avatarImage: 'https://flowbite.com/docs/images/people/profile-picture-4.jpg'
			},
			date: 'Jun. 23, 2022',
			content:
				'Thanks for sharing this. I do came from the Backend development and explored some of the tools to design my Side Projects.',
			childComments: []
		}
		// Add more comments and childComments here
	];
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
			<form>
				<Textarea class="mb-4" placeholder="Write a comment">
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
							name: comment.author.name,
							profilePicture: comment.author.avatarImage
						},
						content: comment.content,
						date: comment.date,
						replies: comment.childComments.map((childComment) => {
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

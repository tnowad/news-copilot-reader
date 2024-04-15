<script lang="ts">
	import '../app.css';
	import { ToastContainer } from 'svelte-toasts';
	import { Toast } from 'flowbite-svelte';
	import {
		CheckCircleSolid,
		ExclamationCircleSolid,
		CloseSolid,
		LightbulbSolid
	} from 'flowbite-svelte-icons';
</script>

<div class="bg-white dark:bg-gray-700 dark:text-white">
	<ToastContainer placement="top-right" let:data>
		<Toast
			class="min-w-64"
			color={data.type == 'info'
				? 'blue'
				: data.type == 'error'
					? 'red'
					: data.type == 'warning'
						? 'orange'
						: data.type == 'success'
							? 'blue'
							: 'gray'}
			dismissable={false}
		>
			<svelte:fragment slot="icon">
				{#if data.type === 'info'}
					<LightbulbSolid class="h-5 w-5" />
					<span class="sr-only">Check icon</span>
				{:else if data.type === 'error'}
					<CloseSolid class="h-5 w-5" />
					<span class="sr-only">Error icon</span>
				{:else if data.type === 'warning'}
					<ExclamationCircleSolid class="h-5 w-5" />
					<span class="sr-only">Warning icon</span>
				{:else if data.type === 'success'}
					<CheckCircleSolid class="h-5 w-5" />
					<span class="sr-only">Check icon</span>
				{/if}
			</svelte:fragment>
			{data.title}
		</Toast>
	</ToastContainer>
	<slot />
</div>

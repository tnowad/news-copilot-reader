<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import * as monaco from 'monaco-editor';
	import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
	import SvelteMarkdown from 'svelte-markdown';

	import { Tabs, TabItem } from 'flowbite-svelte';

	let editorElement: HTMLDivElement;
	let editor: monaco.editor.IStandaloneCodeEditor;
	let model: monaco.editor.ITextModel;
	let source = '';

	function loadCode(code: string, language: string) {
		model = monaco.editor.createModel(code, language);

		editor.setModel(model);
	}

	const generateTextService = {
		generateText: async (text: string) => {
			return { generatedText: text + ' là người kinh doanh.' };
		}
	};

	onMount(async () => {
		self.MonacoEnvironment = {
			getWorker(workerId, label) {
				console.log(workerId, label);
				return new editorWorker();
			}
		};

		monaco.languages.typescript.typescriptDefaults.setEagerModelSync(true);

		monaco.languages.registerInlineCompletionsProvider('markdown', {
			provideInlineCompletions: async function (model, position, context, token) {
				const response = await generateTextService.generateText(
					editor.getValue().split('\n').reverse().pop() ?? ''
				);

				return Promise.resolve({
					items: [
						{
							label: '',
							sortText: '',
							insertText: response.generatedText
						},
						{
							label: '',
							sortText: '',
							insertText:
								'Thủ tướng: Sớm nâng hạng thị trường chứng khoán Việt Nam lên thị trường mới nổi'
						}
					]
				});
			},
			freeInlineCompletions(arg) {}
		});

		editor = monaco.editor.create(editorElement, {
			automaticLayout: true,
			theme: 'vs-dark',
			inlineSuggest: {
				enabled: true,
				showToolbar: 'onHover',
				mode: 'subwordSmart',
				suppressSuggestions: false
			},
			suggest: {
				// preview: true,
				selectionMode: 'whenQuickSuggestion'
			}
		});

		editor.onDidChangeModelContent(() => {
			source = editor.getValue();
		});

		loadCode('# News Copilot\n', 'markdown');
	});

	onDestroy(() => {
		monaco?.editor.getModels().forEach((model) => model.dispose());
		editor?.dispose();
	});
</script>

<Tabs style="full">
	<TabItem open title="Article Editor">
		<div class="h-screen" bind:this={editorElement} />
	</TabItem>
	<TabItem title="Preview">
		<SvelteMarkdown {source} />
	</TabItem>
</Tabs>

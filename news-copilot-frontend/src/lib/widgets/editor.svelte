<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import * as monaco from 'monaco-editor';
	import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
	import generateService from '$lib/services/generate.service';
	import { StatusCodes } from 'http-status-codes';

	let editorElement: HTMLDivElement;
	let editor: monaco.editor.IStandaloneCodeEditor;
	let model: monaco.editor.ITextModel;
	export let content = '';

	function loadCode(code: string, language: string) {
		model = monaco.editor.createModel(code, language);
		editor.setModel(model);
	}

	async function generateText(text: string) {
		const response = await generateService.generateText({
			prompt: text,
			maxLength: text.length + 10,
			temperature: 0.9
		});
		return response;
	}

	onMount(async () => {
		self.MonacoEnvironment = {
			getWorker(workerId, label) {
				return new editorWorker();
			}
		};

		monaco.languages.registerInlineCompletionsProvider('markdown', {
			provideInlineCompletions: async function (model, position, context, token) {
				const result = await generateText(model.getValue().slice(0, model.getOffsetAt(position)));
				switch (result.statusCode) {
					case StatusCodes.OK:
						console.log({
							model: model.getValue(),
							result: result.data.generatedText,
							modelLength: model.getValue().length,
							resultLength: result.data.generatedText.length
						});

						return Promise.resolve({
							items: [
								{
									insertText: result.data.generatedText.slice(model.getValue().length),
									range: new monaco.Range(
										position.lineNumber,
										position.column,
										position.lineNumber,
										position.column
									)
								}
							]
						});
					default:
						return Promise.resolve({
							items: []
						});
				}
			},
			freeInlineCompletions(arg) {}
		});

		editor = monaco.editor.create(editorElement, {
			automaticLayout: true,
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

		editor.onDidChangeModelContent((e) => {
			for (const change of e.changes) {
			}
			content = editor.getValue();
		});

		// Load initial content
		loadCode(content, 'markdown');
	});

	onDestroy(() => {
		monaco?.editor.getModels().forEach((model) => model.dispose());
		editor?.dispose();
	});
</script>

<div class="h-[70vh]" bind:this={editorElement} />

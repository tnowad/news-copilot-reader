<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import * as monaco from 'monaco-editor';
	import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
	import generateService from '$lib/services/generate.service';

	let editorElement: HTMLDivElement;
	let editor: monaco.editor.IStandaloneCodeEditor;
	let model: monaco.editor.ITextModel;
	export let content = '';
	export let articleContext: string = 'news'; // Allow context to be passed from parent

	// Article completion settings
	let completionEnabled = true;
	let completionDelay = 1000;

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
				try {
					if (!completionEnabled) {
						return Promise.resolve({ items: [] });
					}
					
					const currentText = model.getValue();
					const cursorOffset = model.getOffsetAt(position);
					
					// Don't provide completions for very short content
					if (currentText.trim().length < 10) {
						return Promise.resolve({ items: [] });
					}
					
					// Use the new smart completion function with dynamic context
					const completion = await generateService.getSmartCompletion(
						currentText,
						cursorOffset,
						articleContext
					);
					
					if (completion && completion.length > 0) {
						return Promise.resolve({
							items: [
								{
									insertText: completion,
									range: new monaco.Range(
										position.lineNumber,
										position.column,
										position.lineNumber,
										position.column
									),
									kind: monaco.languages.CompletionItemKind.Text,
									detail: `AI-powered ${articleContext} completion`,
									documentation: 'Press Tab to accept this AI-generated completion'
								}
							]
						});
					}
					
					return Promise.resolve({ items: [] });
				} catch (error) {
					console.error('Inline completion error:', error);
					return Promise.resolve({ items: [] });
				}
			},
			freeInlineCompletions(completions) {
				// Cleanup if needed
			}
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

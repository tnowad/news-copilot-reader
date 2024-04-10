<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import * as monaco from 'monaco-editor';
	import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';

	let editorElement: HTMLDivElement;
	let editor: monaco.editor.IStandaloneCodeEditor;
	let model: monaco.editor.ITextModel;
	export let content = '';

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
		editor = monaco.editor.create(editorElement, {
			automaticLayout: true,
			// theme: 'vs-dark',
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
				console.log(change);
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

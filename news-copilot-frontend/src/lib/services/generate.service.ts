import { StatusCodes } from 'http-status-codes';

type GenerateTextParams = {
	prompt: string;
	maxLength?: number;
	temperature?: number;
	topK?: number;
};

type GenerateTextResponse =
	| {
			statusCode: StatusCodes.OK;
			data: {
				generatedText: string;
			};
			message: string;
	  }
	| {
			statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
			message: string;
			error: string;
	  };

const generateTextCache: Record<string, string> = {}; // Simple in-memory cache
let debounceTimeout: NodeJS.Timeout | null = null;

const generateText = async (params: GenerateTextParams, headers: HeadersInit = {}) => {
	const { prompt } = params;

	if (generateTextCache[prompt]) {
		return { statusCode: StatusCodes.OK, data: { generatedText: generateTextCache[prompt] } };
	}

	try {
		const { maxLength = 10, temperature = 0.1, topK = 1 } = params;
		const url = new URL('/api/generate-text', window.location.origin);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify({ prompt, maxLength, temperature, topK }),
			headers: { 'Content-Type': 'application/json', ...headers }
		};

		const response = await fetch(url, requestInit);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const responseData: GenerateTextResponse = await response.json();

		if (responseData.statusCode === StatusCodes.OK) {
			generateTextCache[prompt] = responseData.data.generatedText;
		}

		return responseData;
	} catch (error) {
		throw new Error('Failed to generate text: ' + (error as Error).message);
	}
};

const debouncedGenerateText = (params: GenerateTextParams, headers?: HeadersInit) => {
	return new Promise<GenerateTextResponse>((resolve, reject) => {
		if (debounceTimeout) {
			clearTimeout(debounceTimeout);
		}

		debounceTimeout = setTimeout(async () => {
			try {
				const response = await generateText(params, headers);
				resolve(response);
			} catch (error) {
				reject(error);
			} finally {
				debounceTimeout = null;
			}
		}, 2000);
	});
};

const generateService = {
	generateText: debouncedGenerateText
};

export default generateService;

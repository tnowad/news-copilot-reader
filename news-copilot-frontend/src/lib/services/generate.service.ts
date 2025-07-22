import { StatusCodes } from 'http-status-codes';

// Type definitions for the improved generation service
type GenerateTextParams = {
	prompt: string;
	maxLength?: number;
	temperature?: number;
	topK?: number;
	topP?: number;
};

type CompleteArticleParams = {
	content: string;
	context?: 'news' | 'sports' | 'technology' | 'politics' | 'business' | 'health' | 'entertainment';
	maxTokens?: number;
	temperature?: number;
	style?: 'formal' | 'casual' | 'breaking' | 'analysis';
	generateHeadline?: boolean;
};

type GenerateHeadlineParams = {
	content: string;
	style?: 'breaking' | 'update' | 'analysis' | 'exclusive' | 'standard';
	maxLength?: number;
};

type ContinueStoryParams = {
	previousParagraphs: string[];
	context?: string;
	targetLength?: 'short' | 'medium' | 'long';
	tone?: 'neutral' | 'urgent' | 'analytical';
};

// Response types
type GenerateTextResponse = 
	| {
			statusCode: StatusCodes.OK;
			data: {
				generatedText: string;
				prompt: string;
				parameters: {
					maxLength: number;
					temperature: number;
					topK: number;
					topP: number;
				};
			};
			message: string;
	  }
	| {
			statusCode: StatusCodes.BAD_REQUEST | StatusCodes.INTERNAL_SERVER_ERROR;
			message: string;
			error: string;
	  };

type CompleteArticleResponse = 
	| {
			statusCode: StatusCodes.OK;
			data: {
				originalContent: string;
				completedContent: string;
				headline?: string;
				statistics: {
					originalLength: number;
					generatedLength: number;
					totalLength: number;
				};
				metadata: {
					context: string;
					method: string;
					temperature: number;
					maxTokens: number;
					timestamp: string;
				};
			};
			message: string;
	  }
	| {
			statusCode: StatusCodes.BAD_REQUEST | StatusCodes.INTERNAL_SERVER_ERROR;
			message: string;
			error?: string;
	  };

type GenerateHeadlineResponse = 
	| {
			statusCode: StatusCodes.OK;
			data: {
				headline: string;
				style: string;
				length: number;
			};
			message: string;
	  }
	| {
			statusCode: StatusCodes.BAD_REQUEST | StatusCodes.INTERNAL_SERVER_ERROR;
			message: string;
			error?: string;
	  };

type ServiceStatusResponse = {
	statusCode: StatusCodes.OK;
	data: {
		modelStatus: string;
		cacheEnabled: boolean;
		timestamp: string;
	};
	message: string;
};

// Cache and debouncing
const generateTextCache: Record<string, string> = {};
let debounceTimeout: NodeJS.Timeout | null = null;

// Core generation function (legacy compatibility)
const generateText = async (params: GenerateTextParams, headers: HeadersInit = {}): Promise<GenerateTextResponse> => {
	const { prompt, maxLength = 50, temperature = 0.7, topK = 20, topP = 0.9 } = params;

	// Check cache first
	const cacheKey = `${prompt}-${maxLength}-${temperature}`;
	if (generateTextCache[cacheKey]) {
		return {
			statusCode: StatusCodes.OK,
			data: {
				generatedText: generateTextCache[cacheKey],
				prompt,
				parameters: { maxLength, temperature, topK, topP }
			},
			message: 'Text generated successfully (cached)'
		};
	}

	try {
		const url = new URL('/api/generate-text', window.location.origin);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify({ prompt, maxLength, temperature, topK, topP }),
			headers: { 'Content-Type': 'application/json', ...headers }
		};

		const response = await fetch(url, requestInit);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const responseData: GenerateTextResponse = await response.json();

		if (responseData.statusCode === StatusCodes.OK) {
			generateTextCache[cacheKey] = responseData.data.generatedText;
		}

		return responseData;
	} catch (error) {
		return {
			statusCode: StatusCodes.INTERNAL_SERVER_ERROR,
			message: 'Text generation failed',
			error: (error as Error).message
		};
	}
};

// Advanced article completion
const completeArticle = async (params: CompleteArticleParams, headers: HeadersInit = {}): Promise<CompleteArticleResponse> => {
	try {
		const {
			content,
			context = 'news',
			maxTokens = 100,
			temperature = 0.7,
			style = 'formal',
			generateHeadline = false
		} = params;

		const url = new URL('/api/complete-article', window.location.origin);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
				content,
				context,
				maxTokens,
				temperature,
				style,
				generateHeadline
			}),
			headers: { 'Content-Type': 'application/json', ...headers }
		};

		const response = await fetch(url, requestInit);
		const responseData: CompleteArticleResponse = await response.json();

		return responseData;
	} catch (error) {
		return {
			statusCode: StatusCodes.INTERNAL_SERVER_ERROR,
			message: 'Article completion failed',
			error: (error as Error).message
		};
	}
};

// Generate headlines
const generateHeadline = async (params: GenerateHeadlineParams, headers: HeadersInit = {}): Promise<GenerateHeadlineResponse> => {
	try {
		const { content, style = 'standard', maxLength = 100 } = params;

		const url = new URL('/api/generate-headline', window.location.origin);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify({ content, style, maxLength }),
			headers: { 'Content-Type': 'application/json', ...headers }
		};

		const response = await fetch(url, requestInit);
		const responseData: GenerateHeadlineResponse = await response.json();

		return responseData;
	} catch (error) {
		return {
			statusCode: StatusCodes.INTERNAL_SERVER_ERROR,
			message: 'Headline generation failed',
			error: (error as Error).message
		};
	}
};

// Continue story functionality
const continueStory = async (params: ContinueStoryParams, headers: HeadersInit = {}) => {
	try {
		const {
			previousParagraphs,
			context = 'news',
			targetLength = 'medium',
			tone = 'neutral'
		} = params;

		const url = new URL('/api/continue-story', window.location.origin);
		const requestInit: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
				previousParagraphs,
				context,
				targetLength,
				tone
			}),
			headers: { 'Content-Type': 'application/json', ...headers }
		};

		const response = await fetch(url, requestInit);
		return await response.json();
	} catch (error) {
		return {
			statusCode: StatusCodes.INTERNAL_SERVER_ERROR,
			message: 'Story continuation failed',
			error: (error as Error).message
		};
	}
};

// Get service status
const getServiceStatus = async (): Promise<ServiceStatusResponse> => {
	try {
		const url = new URL('/api/service-status', window.location.origin);
		const response = await fetch(url);
		return await response.json();
	} catch (error) {
		return {
			statusCode: StatusCodes.INTERNAL_SERVER_ERROR,
			data: {
				modelStatus: 'unavailable',
				cacheEnabled: false,
				timestamp: new Date().toISOString()
			},
			message: 'Service status unavailable'
		};
	}
};

// Debounced text generation (legacy compatibility)
const debouncedGenerateText = (params: GenerateTextParams, headers?: HeadersInit): Promise<GenerateTextResponse> => {
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
		}, 1000); // Reduced debounce time for better UX
	});
};

// Smart completion for editor integration
const getSmartCompletion = async (
	currentText: string,
	cursorPosition: number,
	context: string = 'news'
): Promise<string> => {
	try {
		// Extract text up to cursor position
		const textBeforeCursor = currentText.substring(0, cursorPosition);
		
		// Don't complete if we're in the middle of a word
		if (textBeforeCursor.length > 0 && !/\s$/.test(textBeforeCursor)) {
			return '';
		}

		// Get completion
		const result = await completeArticle({
			content: textBeforeCursor,
			context: context as any,
			maxTokens: 30,
			temperature: 0.6
		});

		if (result.statusCode === StatusCodes.OK) {
			const completion = result.data.completedContent.substring(textBeforeCursor.length);
			return completion.trim();
		}

		return '';
	} catch (error) {
		console.error('Smart completion error:', error);
		return '';
	}
};

// Export the service
const generateService = {
	// Legacy compatibility
	generateText: debouncedGenerateText,
	
	// New advanced features
	completeArticle,
	generateHeadline,
	continueStory,
	getServiceStatus,
	getSmartCompletion,
	
	// Utility functions
	clearCache: () => {
		Object.keys(generateTextCache).forEach(key => delete generateTextCache[key]);
	},
	
	// Health check
	healthCheck: async () => {
		try {
			const status = await getServiceStatus();
			return status.statusCode === StatusCodes.OK;
		} catch {
			return false;
		}
	}
};

export default generateService;

// Export types for use in components
export type {
	GenerateTextParams,
	CompleteArticleParams,
	GenerateHeadlineParams,
	ContinueStoryParams,
	GenerateTextResponse,
	CompleteArticleResponse,
	GenerateHeadlineResponse
};

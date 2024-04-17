import type { StatusCodes } from 'http-status-codes';
import { API_URL } from '$env/static/private';

type Statistics = {
	totalArticles: number;
	totalViews: number;
	totalComments: number;
};

type CategoryArticleCount = {
	category: string;
	count: number;
};

type ApexOptions = {
	chart: {
		type: string;
	};
	series: {
		name: string;
		data: number[];
	}[];
	xaxis: {
		categories: string[];
	};
	title: {
		text: string;
	};
};

type ArticlesStatisticsResponse = {
	statusCode: StatusCodes.OK;
	data: Statistics;
	message: string;
};

type CategoryArticleCountResponse = {
	statusCode: StatusCodes.OK;
	data: ApexOptions;
	message: string;
};

const getArticlesStatistics = async (): Promise<ArticlesStatisticsResponse> => {
	try {
		const url = new URL('/statistics/articles', API_URL);
		const response = await fetch(url);
		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch articles statistics: ' + (error as Error).message);
	}
};

const getCategoryArticleCount = async (): Promise<CategoryArticleCountResponse> => {
	try {
		const url = new URL('/statistics/categories-articles', API_URL);
		const response = await fetch(url);
		return response.json();
	} catch (error) {
		throw new Error('Failed to fetch category article count: ' + (error as Error).message);
	}
};

const statisticsService = {
	getArticlesStatistics,
	getCategoryArticleCount
};

export default statisticsService;

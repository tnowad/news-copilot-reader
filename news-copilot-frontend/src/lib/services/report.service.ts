import type { StatusCodes } from 'http-status-codes';
import { defaultHeaders } from './config';
import { API_URL } from '$env/static/private';
import type { Report } from './types';


type CreateReportBody = {
    content: string;
    objectId: number;
    objectType: 'Article' | 'User' | 'Comment';
};

type CreateReportSuccessful = {
    statusCode: StatusCodes.CREATED;
    data: {
        report: Report;
    };
    message: string;
};

type CreateReportServerError = {
    statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
    message: string;
    error: string;
};

type CreateReportResponse = Omit<Response, 'json'> & {
    json: () => Promise<CreateReportSuccessful | CreateReportServerError>;
};

const createReport = async (body: CreateReportBody, headers: HeadersInit = {}) => {
    try {
        const url = new URL('/reports', API_URL);
        const requestInit: RequestInit = {
            method: 'POST',
            body: JSON.stringify(body),
            headers: { ...defaultHeaders, ...headers }
        };

        const response = (await fetch(url, requestInit)) as CreateReportResponse;

        return response.json();
    } catch (error) {
        throw new Error('Failed to create report: ' + (error as Error).message);
    }
};

type GetAllReportsParams = {
    limit?: number;
    page?: number;
    search?: string;
    sortBy?: 'createdAt';
    sortOrder?: 'asc' | 'desc';
};

type GetAllReportsSuccessful = {
    statusCode: StatusCodes.OK;
    data: {
        report: Report[];
        metadata: {
            pagination: {
                offset: number;
                limit: number;
                previousOffset: number;
                nextOffset: number;
                currentPage: number;
                totalCount: number;
            };
            sortedBy: {
                name: 'date' | 'name';
                sortOrder: 'asc' | 'desc';
            };
            filter: {
                articleId: string;
                userId: string;
                parentId: string;
                search: string;
            };
        };
        message: string;
    };
};

type GetAllReportsServerError = {
    statusCode: StatusCodes.INTERNAL_SERVER_ERROR;
    message: string;
    error: string;
};

type GetAllReportsResponse = Omit<Response, 'json'> & {
    json: () => Promise<GetAllReportsSuccessful | GetAllReportsServerError>;
};

const getAllReports = async (params: GetAllReportsParams, headers: HeadersInit = {}) => {
    try {
        const { page, limit, search, sortBy, sortOrder } = params;
        const url = new URL('/reports', API_URL);
        const queryParams = new URLSearchParams();

        if (page) queryParams.set('page', page.toString());
        if (limit) queryParams.set('limit', limit.toString());
        if (search) queryParams.set('search', search);
        if (sortBy) queryParams.set('sortBy', sortBy);
        if (sortOrder) queryParams.set('sortOrder', sortOrder);

        url.search = queryParams.toString();
        const requestInit: RequestInit = {
            method: 'GET',
            headers: { ...defaultHeaders, ...headers }
        };

        const response = (await fetch(url, requestInit)) as GetAllReportsResponse;

        return response.json();
    } catch (error) {
        throw new Error('Failed to get report: ' + (error as Error).message);
    }
};

const reportService = {
    createReport,
    getAllReports
}
export default reportService
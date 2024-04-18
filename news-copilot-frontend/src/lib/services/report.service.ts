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

const reportService = {
    createReport
}
export default reportService
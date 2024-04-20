import reportService from '$lib/services/report.service';
import { redirect } from '@sveltejs/kit';
import { StatusCodes } from 'http-status-codes';
import type { Actions } from './$types';

export const load = async (event) => {
    if (!event.locals.user.roles?.some((role) => role == 'ADMIN')) {
        redirect(StatusCodes.TEMPORARY_REDIRECT, '/');
    }

    const page = parseInt(event.url.searchParams.get('page') ?? 1);
    const limit = parseInt(event.url.searchParams.get('limit') ?? 10);
    const search = event.url.searchParams.get('search') ?? '';

    const reportsResponse = await reportService.getAllReports({
        page: page,
        limit: limit,
        search: search
    });
    console.log(reportsResponse.data.reports);

    return {
        reports: reportsResponse.statusCode === StatusCodes.OK ? reportsResponse.data.reports : [],
        metadata: reportsResponse.statusCode === StatusCodes.OK ? reportsResponse.data.metadata : null
    };
};
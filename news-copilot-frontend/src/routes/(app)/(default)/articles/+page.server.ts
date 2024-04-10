import type { Actions } from "@sveltejs/kit";
import artcileService from "$lib/services/article.service";
import { StatusCodes } from "http-status-codes";
export const actions = {
    default: async (event) => {
        const articleResponse = await artcileService.getAllArticles({ limit: 20 })
        const articles = articleResponse.statusCode === StatusCodes.OK ? articleResponse.data.articles : [];
        return articles
    }
} satisfies Actions;

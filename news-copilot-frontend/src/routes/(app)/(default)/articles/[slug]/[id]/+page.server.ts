import type { PageServerLoad } from './$types';
import articleService from '$lib/services/article.service';
import { StatusCodes } from 'http-status-codes';

export const load: PageServerLoad = async ({params}) => {
    const {id} = params; 
  const intId = parseInt(id, 10);
  console.log(intId + ' loaded');

  
  const articlesResponse = await articleService.getAllArticles()
  const articles = articlesResponse.statusCode === StatusCodes.OK ? articlesResponse.data.articles : []
  const matchingArticle = articles.find(article => article.id === intId);
  console.log(matchingArticle)
    return {article : matchingArticle}
  
};
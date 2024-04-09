from http import HTTPStatus

from flask import Blueprint, jsonify, request

from app.models.article import Article
from app.services.recommender.recommender import hybrid_recommender

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("/recommendations/articles", methods=["GET"])
def get_recommendations_articles():
    user_id = request.args.get("userId", type=int)
    article_id = request.args.get("articleId", type=int)
    limit = request.args.get("limit", type=int) or 10
    style = request.args.get("style", type=str) or "compact"
    includes = request.args.getlist("includes", type=str)

    recommendations_data = hybrid_recommender.recommend_articles(
        user_id, article_id, limit
    )

    articles = Article.query.filter(Article.id.in_(recommendations_data)).all()

    articles_data = []
    for article in articles:
        article_info = {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "coverImage": article.cover_image,
            "slug": article.slug,
            "createdAt": article.created_at,
        }

        if style == "full":
            article_info["content"] = article.content
            article_info["updatedAt"] = article.updated_at
            article_info["deletedAt"] = article.deleted_at

        if "comments" in includes:
            article_info["comments"] = [
                {
                    "id": comment.id,
                    "content": comment.content,
                    "createdAt": comment.created_at,
                    "updatedAt": comment.updated_at,
                    "parentCommentId": comment.parent_id,
                    "author": {
                        "id": comment.author.id,
                        "email": comment.author.email,
                        "displayName": comment.author.display_name,
                        "avatarImage": comment.author.avatar_image,
                    },
                }
                for comment in article.comments
            ]

        if "categories" in includes:
            article_info["categories"] = [
                {
                    "id": category.id,
                    "title": category.title,
                    "slug": category.slug,
                }
                for category in article.categories
            ]

        if "author" in includes:
            article_info["author"] = {
                "id": article.author.id,
                "email": article.author.email,
                "displayName": article.author.display_name,
                "avatarImage": article.author.avatar_image,
            }

        articles_data.append(article_info)

    metadata = {
        "pagination": {
            "limit": limit,
        },
        "style": style,
        "includes": includes,
        "filters": {
            "userId": user_id,
            "articleId": article_id,
        },
    }

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "Get all articles route",
        "data": {"articles": articles_data, "metadata": metadata},
    }

    return jsonify(response_data), HTTPStatus.OK

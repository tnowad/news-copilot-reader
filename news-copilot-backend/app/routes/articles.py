from http import HTTPStatus
from flask import Blueprint, jsonify, request

from app.models.article import Article
from typing import List

articles_bp = Blueprint("articles", __name__)


@articles_bp.route("/articles", methods=["GET"])
def get_articles():
    articles: List[Article] = Article.query.all()
    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "message": "Get all articles route",
                "data": {
                    "articles": [
                        {
                            "id": article.id,
                        }
                        for article in articles
                    ]
                },
            }
        ),
        HTTPStatus.OK,
    )


@articles_bp.route("/articles", methods=["POST"])
def create_article():
    data = request.json

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.CREATED,
                "message": "Article created successfully",
                "data": {
                    "article": {
                        "id": 1,
                    },
                },
            }
        ),
        HTTPStatus.CREATED,
    )


@articles_bp.route("/articles/<int:article_id>", methods=["PUT"])
def update_article(article_id):
    data = request.json
    if article_id is None:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Article ID is required",
                    "errors": [
                        {"field": "id", "message": "Article ID is required"},
                    ],
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    article = Article.query.get(article_id)
    if article is None:
        return (
            jsonify(
                {"statusCode": HTTPStatus.NOT_FOUND, "message": "Article not found"}
            ),
            HTTPStatus.NOT_FOUND,
        )

    article.save()

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "message": "Article updated successfully",
                "data": {
                    "article": {
                        "id": 1,
                    }
                },
            }
        ),
        HTTPStatus.OK,
    )


@articles_bp.route("/articles/<int:article_id>", methods=["DELETE"])
def delete_article(article_id):
    data = request.json
    if article_id is None:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Article ID is required",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    # Assuming there's a method to get article by ID from the database
    article = Article.query.get(article_id)
    if article is None:
        return (
            jsonify(
                {"statusCode": HTTPStatus.NOT_FOUND, "message": "Article not found"}
            ),
            HTTPStatus.NOT_FOUND,
        )

    # Assuming there's a method to delete the article from the database
    article.delete()

    return (
        jsonify(
            {"statusCode": HTTPStatus.OK, "message": "Article deleted successfully"}
        ),
        HTTPStatus.OK,
    )


@articles_bp.route("/articles/<int:article_id>", methods=["GET"])
def get_article(article_id):
    data = request.json
    if article_id is None:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Article ID is required",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    # Assuming there's a method to get article by ID from the database
    article = Article.query.get(article_id)
    if article is None:
        return (
            jsonify(
                {"statusCode": HTTPStatus.NOT_FOUND, "message": "Article not found"}
            ),
            HTTPStatus.NOT_FOUND,
        )

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "message": f"Get article with id {article_id} route",
                "data": article.to_dict(),
            }
        ),
        HTTPStatus.OK,
    )

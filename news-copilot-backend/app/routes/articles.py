from http import HTTPStatus
from typing import List

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.decorators.authorization import role_required
from app.extensions import db
from app.models.article import Article
from app.models.category import Category
from app.models.role import RoleEnum
from app.models.user import User

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
@jwt_required()
@role_required([RoleEnum.ADMIN, RoleEnum.WRITER])
def create_article():
    current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()

    data = request.get_json()
    title = data.get("title")
    cover_image = data.get("coverImage")
    summary = data.get("summary")
    slug = data.get("slug")
    content = data.get("content")
    category_ids = data.get("categoryIds", [])
    author_id = data.get("authorId")

    if (
        not any(role.name == RoleEnum.ADMIN for role in current_user.roles)
        and author_id != current_user.id
    ):
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.FORBIDDEN,
                    "message": "Only users with ADMIN role can create articles with custom author",
                    "errors": [
                        {
                            "field": "authorId",
                            "message": "Only users with ADMIN role can create articles with custom author",
                        }
                    ],
                },
            ),
            HTTPStatus.FORBIDDEN,
        )

    author_id = current_user.id

    article = Article(
        title=title,
        cover_image=cover_image,
        summary=summary,
        slug=slug,
        content=content,
    )

    article.author_id = author_id

    for category_id in category_ids:
        category = Category.query.get(category_id)
        if category:
            article.categories.append(category)

    db.session.add(article)
    db.session.commit()

    response_data = {
        "statusCode": HTTPStatus.CREATED,
        "message": "Article created successfully",
        "data": {
            "article": article,
        },
    }

    return jsonify(response_data), HTTPStatus.CREATED


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

from datetime import datetime
from http import HTTPStatus
from typing import List

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.decorators.authorization import role_required
from app.extensions import db
from app.models.article import Article
from app.models.bookmark import Bookmark
from app.models.category import Category
from app.models.role import RoleEnum
from app.models.user import User

articles_bp = Blueprint("articles", __name__)


@articles_bp.route("/articles", methods=["GET"])
def get_articles():
    try:
        page = request.args.get("page", type=int) or 1
        limit = request.args.get("limit", type=int) or 10
        search = request.args.get("search", type=str)
        category_ids = request.args.getlist("categoryIds", type=int)
        sort_by = request.args.get("sortBy", type=str)
        sort_order = request.args.get("sortOrder", type=str)
        style = request.args.get("style", type=str)
        includes = request.args.getlist("includes", type=str)

        # Query articles based on parameters
        query = Article.query
        query = query.filter(Article.deleted_at.is_(None))

        if search:
            query = query.filter(Article.title.ilike(f"%{search}%"))  # pyright: ignore
        if category_ids:
            query = query.join(Article.categories).filter(Category.id.in_(category_ids))

        if sort_by:
            if sort_by == "title":
                query = query.order_by(Article.title)  # pyright: ignore
            elif sort_by == "created_at":
                query = query.order_by(Article.created_at)

        if sort_order:
            if sort_order == "desc":
                query = query.order_by(Article.title.desc())  # pyright: ignore
            elif sort_order == "asc":
                query = query.order_by(Article.title.asc())  # pyright: ignore

        total_articles = query.count()

        if page and limit:
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

        articles = query.all()

        # Construct response data

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

        # Construct metadata
        metadata = {
            "pagination": {
                "offset": (page - 1) * limit if (page and limit) else None,
                "limit": limit,
                "previousOffset": (page - 2) * limit if page > 1 else None,
                "nextOffset": page * limit if articles else None,
                "currentPage": page if page else None,
                "pageCount": total_articles // limit if page and limit else None,
                "totalCount": total_articles,
            },
            "sortedBy": {"name": sort_by, "order": sort_order},
            "style": style,
            "filters": {
                "search": search,
                "categoryIds": category_ids,
            },
        }

        # Construct final response
        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Get all articles route",
            "data": {"articles": articles_data, "metadata": metadata},
        }

        return jsonify(response_data), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "message": "Internal Server Error",
                    "error": str(e),
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@articles_bp.route("/articles/<int:article_id>", methods=["GET"])
def get_article(article_id):
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

    article = Article.query.get(article_id)
    if article is None:
        return (
            jsonify(
                {"statusCode": HTTPStatus.NOT_FOUND, "message": "Article not found"}
            ),
            HTTPStatus.NOT_FOUND,
        )

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": f"Get article with id {article_id} route",
        "data": {
            "article": {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "coverImage": article.cover_image,
                "slug": article.slug,
            }
        },
    }

    style_param = request.args.get("style")
    includes_param = request.args.getlist("includes")

    if "categories" in includes_param:
        response_data["data"]["article"]["categories"] = [
            {
                "id": category.id,
                "title": category.title,
                "slug": category.slug,
            }
            for category in article.categories
        ]

    if "author" in includes_param:
        response_data["data"]["article"]["author"] = {
            "id": article.author.id,
            "email": article.author.email,
            "displayName": article.author.display_name,
            "avatarImage": article.author.avatar_image,
        }

    if "comments" in includes_param:
        response_data["data"]["article"]["comments"] = [
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

    if style_param == "full":
        response_data["data"]["article"]["createdAt"] = article.created_at
        response_data["data"]["article"]["updatedAt"] = article.updated_at
        response_data["data"]["article"]["deletedAt"] = article.deleted_at
        response_data["data"]["article"]["content"] = article.content

    return (
        jsonify(response_data),
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
            "article": {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "coverImage": article.cover_image,
                "slug": article.slug,
                "author": {
                    "id": article.author.id,
                    "email": article.author.email,
                    "displayName": article.author.display_name,
                    "avatarImage": article.author.avatar_image,
                },
                "categories": [
                    {
                        "id": category.id,
                        "title": category.title,
                        "slug": category.slug,
                    }
                    for category in article.categories
                ],
            },
        },
    }

    return jsonify(response_data), HTTPStatus.CREATED


@articles_bp.route("/articles/<int:article_id>", methods=["PUT"])
@jwt_required()
@role_required([RoleEnum.ADMIN, RoleEnum.WRITER])
def update_article(article_id):
    data = request.get_json()
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

    title = data.get("title")
    cover_image = data.get("coverImage")
    summary = data.get("summary")
    slug = data.get("slug")
    content = data.get("content")
    category_ids = data.get("categoryIds", [])
    author_id = data.get("authorId")

    if title:
        article.title = title

    if cover_image:
        article.cover_image = cover_image

    if summary:
        article.summary = summary

    if slug:
        article.slug = slug

    if content:
        article.content = content

    if author_id:
        current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()
        if (
            not any(role.name == RoleEnum.ADMIN for role in current_user.roles)
            and author_id != current_user.id
        ):
            return (
                jsonify(
                    {
                        "statusCode": HTTPStatus.FORBIDDEN,
                        "message": "Only users with ADMIN role can update articles with custom author",
                        "errors": [
                            {
                                "field": "authorId",
                                "message": "Only users with ADMIN role can update articles with custom author",
                            }
                        ],
                    },
                ),
                HTTPStatus.FORBIDDEN,
            )
        article.author_id = author_id

    if category_ids:
        article.categories.clear()
        for category_id in category_ids:
            category = Category.query.get(category_id)
            if category:
                article.categories.append(category)

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "Article updated successfully",
        "data": {
            "article": {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "coverImage": article.cover_image,
                "slug": article.slug,
                "content": article.content,
                "author": {
                    "id": article.author.id,
                    "email": article.author.email,
                    "displayName": article.author.display_name,
                    "avatarImage": article.author.avatar_image,
                },
                "categories": [
                    {
                        "id": category.id,
                        "title": category.title,
                        "slug": category.slug,
                    }
                    for category in article.categories
                ],
            }
        },
    }

    db.session.commit()
    db.session.close()

    return (
        jsonify(response_data),
        HTTPStatus.OK,
    )


@articles_bp.route("/articles/<int:article_id>", methods=["DELETE"])
@jwt_required()
@role_required([RoleEnum.ADMIN, RoleEnum.WRITER])
def delete_article(article_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()
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

    article = Article.query.get(article_id)
    if article is None or article.deleted_at is not None:
        return (
            jsonify(
                {"statusCode": HTTPStatus.NOT_FOUND, "message": "Article not found"}
            ),
            HTTPStatus.NOT_FOUND,
        )

    if article.author_id != current_user.id and not any(
        role.name == RoleEnum.ADMIN for role in current_user.roles
    ):
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.FORBIDDEN,
                    "message": "You are not allowed to delete this article",
                }
            ),
            HTTPStatus.FORBIDDEN,
        )

    article.deleted_at = datetime.now()
    db.session.commit()
    db.session.close()

    return (
        jsonify(
            {"statusCode": HTTPStatus.OK, "message": "Article deleted successfully"}
        ),
        HTTPStatus.OK,
    )


@articles_bp.route("/articles/bookmarks", methods=["GET"])
@jwt_required()
def get_bookmarked_articles():
    try:
        page = request.args.get("page", type=int) or 1
        limit = request.args.get("limit", type=int) or 10
        sort_by = request.args.get("sortBy", type=str)
        sort_order = request.args.get("sortOrder", type=str)
        style = request.args.get("style", type=str)
        includes = request.args.getlist("includes", type=str)

        user = User.query.filter_by(email=get_jwt_identity()).first_or_404()
        bookmarks = user.bookmarks
        articles = [bookmark.article for bookmark in bookmarks]
        total_articles = len(articles)

        # Construct response data

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

        # Construct metadata
        metadata = {
            "pagination": {
                "offset": (page - 1) * limit if (page and limit) else None,
                "limit": limit,
                "previousOffset": (page - 2) * limit if page > 1 else None,
                "nextOffset": page * limit if articles else None,
                "currentPage": page if page else None,
                "pageCount": total_articles // limit if page and limit else None,
                "totalCount": total_articles,
            },
            "sortedBy": {"name": sort_by, "order": sort_order},
            "style": style,
        }

        # Construct final response
        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Get all articles route",
            "data": {"articles": articles_data, "metadata": metadata},
        }

        return jsonify(response_data), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "message": "Internal Server Error",
                    "error": str(e),
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

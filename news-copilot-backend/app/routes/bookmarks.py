from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.decorators.authorization import role_required

from app.extensions import db
from app.models.article import Article
from app.models.bookmark import Bookmark
from app.models.user import User
from app.models.role import RoleEnum
from sqlalchemy import and_

bookmarks_bp = Blueprint("bookmarks", __name__)


# Error handling for "Bookmark not found" error
@bookmarks_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Bookmark not found"}), HTTPStatus.NOT_FOUND


# Error handling for generic internal server errors
@bookmarks_bp.errorhandler(Exception)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), HTTPStatus.INTERNAL_SERVER_ERROR


@bookmarks_bp.route("/bookmarks", methods=["POST"])
@jwt_required()
def create_bookmark():
    data = request.get_json()
    article_id = data.get("article_id")
    current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()

    user_id = current_user.id

    if not User.query.get(user_id):
        return jsonify({"error": "User not found"}), HTTPStatus.NOT_FOUND

    article = Article.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), HTTPStatus.NOT_FOUND

    existing_bookmark = Bookmark.query.filter_by(
        article_id=article_id, user_id=user_id
    ).first()
    if existing_bookmark:
        return jsonify({"error": "Bookmark already exists"}), HTTPStatus.BAD_REQUEST

    bookmark = Bookmark(
        article_id=article_id, user_id=user_id, created_at=datetime.now()
    )
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({"message": "Bookmark created successfully"}), HTTPStatus.CREATED


@bookmarks_bp.route("/bookmarks", methods=["GET"])
@jwt_required()
@role_required([RoleEnum.ADMIN])
def get_bookmarks():
    try:
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first_or_404()

        if RoleEnum.ADMIN in [role for role in current_user.roles]:
            bookmarks = Bookmark.query.all()
        else:
            bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()

        article_id = request.args.get("articleId", type=int)
        limit = request.args.get("limit", type=int) or 10
        style = request.args.get("style", type=str) or "compact"
        includes = request.args.getlist("includes", type=str)

        bookmark_data = []
        for bookmark in bookmarks:
            bookmark_info = {
                "id": bookmark.id,
                "user_id": bookmark.user_id,
                "article": {
                    "id": bookmark.article.id,
                    "title": bookmark.article.title,
                    "summary": bookmark.article.summary,
                    "coverImage": bookmark.article.cover_image,
                    "slug": bookmark.article.slug,
                    "createdAt": bookmark.article.created_at.strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                    "content": bookmark.article.content if style == "full" else None,
                    "updatedAt": (
                        bookmark.article.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                        if style == "full" and bookmark.article.updated_at
                        else None
                    ),
                    "deletedAt": (
                        bookmark.article.deleted_at.strftime("%Y-%m-%dT%H:%M:%S")
                        if style == "full" and bookmark.article.deleted_at
                        else None
                    ),
                    "comments": (
                        [
                            {
                                "id": comment.id,
                                "content": comment.content,
                                "createdAt": comment.created_at.strftime(
                                    "%Y-%m-%dT%H:%M:%S"
                                ),
                                "updatedAt": comment.updated_at.strftime(
                                    "%Y-%m-%dT%H:%M:%S"
                                ),
                                "parentCommentId": comment.parent_id,
                                "author": {
                                    "id": comment.author.id,
                                    "email": comment.author.email,
                                    "displayName": comment.author.display_name,
                                    "avatarImage": comment.author.avatar_image,
                                },
                            }
                            for comment in bookmark.article.comments
                        ]
                        if "comments" in includes
                        else None
                    ),
                    "categories": (
                        [
                            {
                                "id": category.id,
                                "title": category.title,
                                "slug": category.slug,
                            }
                            for category in bookmark.article.categories
                        ]
                        if "categories" in includes
                        else None
                    ),
                    "author": (
                        {
                            "id": bookmark.article.author.id,
                            "email": bookmark.article.author.email,
                            "displayName": bookmark.article.author.display_name,
                            "avatarImage": bookmark.article.author.avatar_image,
                        }
                        if "author" in includes
                        else None
                    ),
                },
                "created_at": bookmark.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            bookmark_data.append(bookmark_info)

        metadata = {
            "pagination": {
                "limit": limit,
            },
            "style": style,
            "includes": includes,
            "filters": {
                "userId": current_user.id,
                "articleId": article_id,
            },
        }

        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Get all bookmarks route",
            "data": {"bookmarks": bookmark_data, "metadata": metadata},
        }

        return jsonify(response_data), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify({"error": "Internal Server Error", "error_detail": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@bookmarks_bp.route("/bookmarks/<int:bookmark_id>", methods=["GET"])
@jwt_required()
def get_bookmark_by_id(bookmark_id):
    try:
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first_or_404()
        bookmark = Bookmark.query.filter_by(
            id=bookmark_id, user_id=current_user.id
        ).first_or_404()

        bookmark_info = {
            "id": bookmark.id,
            "user_id": bookmark.user_id,
            "article": {
                "id": bookmark.article.id,
                "title": bookmark.article.title,
                "summary": bookmark.article.summary,
                "coverImage": bookmark.article.cover_image,
                "slug": bookmark.article.slug,
                "createdAt": bookmark.article.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "content": bookmark.article.content,
                "updatedAt": (
                    bookmark.article.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                    if bookmark.article.updated_at
                    else None
                ),
                "deletedAt": (
                    bookmark.article.deleted_at.strftime("%Y-%m-%dT%H:%M:%S")
                    if bookmark.article.deleted_at
                    else None
                ),
                "comments": [
                    {
                        "id": comment.id,
                        "content": comment.content,
                        "createdAt": comment.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                        "updatedAt": (
                            comment.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                            if comment.updated_at
                            else None
                        ),
                        "parentCommentId": comment.parent_id,
                        "author": {
                            "id": comment.author.id,
                            "email": comment.author.email,
                            "displayName": comment.author.display_name,
                            "avatarImage": comment.author.avatar_image,
                        },
                    }
                    for comment in bookmark.article.comments
                ],
                "categories": [
                    {
                        "id": category.id,
                        "title": category.title,
                        "slug": category.slug,
                    }
                    for category in bookmark.article.categories
                ],
                "author": {
                    "id": bookmark.article.author.id,
                    "email": bookmark.article.author.email,
                    "displayName": bookmark.article.author.display_name,
                    "avatarImage": bookmark.article.author.avatar_image,
                },
            },
            "created_at": bookmark.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        return jsonify({"bookmark": bookmark_info}), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify({"error": "Internal Server Error", "error_detail": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@bookmarks_bp.route("/bookmarks/check-marked", methods=["POST"])
@jwt_required()
def check_marked():
    try:
        data = request.get_json()
        article_ids = data.get("article_ids", [])
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first_or_404()
        user_id = current_user.id

        marked_article = Bookmark.query.filter(
            Bookmark.article.id.in_(article_ids), user_id == user_id
        ).first_or_404()

        bookmark_info = {
            "id": marked_article.id,
            "user_id": marked_article.user_id,
            "article": {
                "id": marked_article.article.id,
                "title": marked_article.article.title,
                "summary": marked_article.article.summary,
                "coverImage": marked_article.article.cover_image,
                "slug": marked_article.article.slug,
                "createdAt": marked_article.article.created_at.strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "content": marked_article.article.content,
                "updatedAt": (
                    marked_article.article.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                    if marked_article.article.updated_at
                    else None
                ),
                "deletedAt": (
                    marked_article.article.deleted_at.strftime("%Y-%m-%dT%H:%M:%S")
                    if marked_article.article.deleted_at
                    else None
                ),
                "comments": [
                    {
                        "id": comment.id,
                        "content": comment.content,
                        "createdAt": comment.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                        "updatedAt": (
                            comment.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                            if comment.updated_at
                            else None
                        ),
                        "parentCommentId": comment.parent_id,
                        "author": {
                            "id": comment.author.id,
                            "email": comment.author.email,
                            "displayName": comment.author.display_name,
                            "avatarImage": comment.author.avatar_image,
                        },
                    }
                    for comment in marked_article.article.comments
                ],
                "categories": [
                    {
                        "id": category.id,
                        "title": category.title,
                        "slug": category.slug,
                    }
                    for category in marked_article.article.categories
                ],
                "author": {
                    "id": marked_article.article.author.id,
                    "email": marked_article.article.author.email,
                    "displayName": marked_article.article.author.display_name,
                    "avatarImage": marked_article.article.author.avatar_image,
                },
            },
            "created_at": marked_article.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        return jsonify({"bookmark": bookmark_info}), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify({"error": "Internal Server Error", "error_detail": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

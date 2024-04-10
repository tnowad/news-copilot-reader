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

bookmarks_bp = Blueprint("bookmarks", __name__)


@bookmarks_bp.route("/bookmarks", methods=["POST"])
@jwt_required()
def create_bookmark():
    data = request.get_json()
    article_id = data.get("article_id")
    current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()

    user_id = current_user.id

    if not User.query.get(user_id):
        return jsonify({"message": "User not found"}), HTTPStatus.NOT_FOUND

    article = Article.query.get(article_id)
    if not article:
        return jsonify({"message": "Article not found"}), HTTPStatus.NOT_FOUND

    existing_bookmark = Bookmark.query.filter_by(
        article_id=article_id, user_id=user_id
    ).first()
    if existing_bookmark:
        return jsonify({"message": "Bookmark already exists"}), HTTPStatus.BAD_REQUEST

    bookmark = Bookmark(
        article_id=article_id, user_id=user_id, created_at=datetime.now()
    )
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({"message": "Bookmark created successfully"}), HTTPStatus.CREATED


@bookmarks_bp.route("/bookmarks", methods=["GET"])
@jwt_required()
def get_bookmarks():
    try:
        current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()

        if current_user.role == RoleEnum.ADMIN:
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
                    "createdAt": bookmark.article.created_at.isoformat(),
                    "content": bookmark.article.content if style == "full" else None,
                    "updatedAt": (
                        bookmark.article.updated_at.isoformat()
                        if style == "full"
                        else None
                    ),
                    "deletedAt": (
                        bookmark.article.deleted_at.isoformat()
                        if style == "full"
                        else None
                    ),
                    "comments": (
                        [
                            {
                                "id": comment.id,
                                "content": comment.content,
                                "createdAt": comment.created_at.isoformat(),
                                "updatedAt": comment.updated_at.isoformat(),
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
                "created_at": bookmark.created_at.isoformat(),
            }
            bookmark_data.append(bookmark_info)

        metadata = {
            "pagination": {
                "limit": limit,
            },
            "style": style,
            "includes": includes,
            "filters": {
                "userId": current_user.id,  # Change from user_id to current_user.id
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
            jsonify({"message": "Internal Server Error", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@bookmarks_bp.route("/bookmarks/<int:bookmark_id>", methods=["GET"])
@jwt_required()
def get_bookmark_by_id(bookmark_id):
    try:
        user_id = get_jwt_identity()
        bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()

        if not bookmark:
            return (
                jsonify(
                    {
                        "message": "Bookmark not found or does not belong to the current user"
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        bookmark_info = {
            "id": bookmark.id,
            "user_id": bookmark.user_id,
            "article": {
                "id": bookmark.article.id,
                "title": bookmark.article.title,
                "summary": bookmark.article.summary,
                "coverImage": bookmark.article.cover_image,
                "slug": bookmark.article.slug,
                "createdAt": bookmark.article.created_at.isoformat(),
                "content": bookmark.article.content,
                "updatedAt": bookmark.article.updated_at.isoformat(),
                "deletedAt": bookmark.article.deleted_at.isoformat(),
                # Assuming you want to include comments, categories, and author information
                "comments": [
                    {
                        "id": comment.id,
                        "content": comment.content,
                        "createdAt": comment.created_at.isoformat(),
                        "updatedAt": comment.updated_at.isoformat(),
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
            "created_at": bookmark.created_at.isoformat(),
        }
        return jsonify({"bookmark": bookmark_info}), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify({"message": "Internal Server Error", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@bookmarks_bp.route("/bookmarks/<int:bookmark_id>", methods=["DELETE"])
@jwt_required()
def delete_bookmark(bookmark_id):
    user_id = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify({"message": "Bookmark not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({"message": "Bookmark deleted successfully"}), HTTPStatus.OK

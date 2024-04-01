from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.article import Article
from app.models.comment import Comment
from app.models.user import User

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/comments", methods=["GET"])
def get_comments():
    try:
        page = request.args.get("page", type=int) or 1
        limit = request.args.get("limit", type=int) or 10
        sort_by = request.args.get("sortBy", type=str)
        sort_order = request.args.get("sortOrder", type=str)
        style = request.args.get("style", type=str)
        includes = request.args.getlist("includes", type=str)
        user_id = request.args.get("userId", type=int)
        article_id = request.args.get("articleId", type=int)
        search = request.args.get("search", type=str)

        query = Comment.query
        query = query.filter(Comment.deleted_at.is_(None))

        if user_id:
            query = query.filter(Comment.author_id == user_id)  # type: ignore

        if article_id:
            query = query.filter(Comment.article_id == article_id)  # type: ignore

        if search:
            query = query.filter(Comment.content.ilike(f"%{search}%"))  # type: ignore

        if sort_by and sort_order:
            if sort_by == "user":
                query = query.join(User).order_by(
                    User.display_name.asc()  # type: ignore
                    if sort_order == "asc"
                    else User.display_name.desc()  # type: ignore
                )
            elif sort_by == "article":
                query = query.join(Article).order_by(
                    Article.title.asc()  # type: ignore
                    if sort_order == "asc"
                    else Article.title.desc()  # type: ignore
                )
            elif sort_by == "createdAt":
                query = query.order_by(
                    Comment.created_at.asc()
                    if sort_order == "asc"
                    else Comment.created_at.desc()
                )

        if page and limit:
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

        comments = query.all()

        comments_data = []
        for comment in comments:
            comment_info = {
                "id": comment.id,
                "content": comment.content,
                "parent_id": comment.parent_id,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            }

            if style == "full":
                comment_info["deleted_at"] = comment.deleted_at

            if "author" in includes and comment.author:
                comment_info["author"] = {
                    "id": comment.author.id,
                    "email": comment.author.email,
                    "displayName": comment.author.display_name,
                    "avatarImage": comment.author.avatar_image,
                }

            if "article" in includes and comment.article:
                comment_info["article"] = {
                    "id": comment.article.id,
                    "title": comment.article.title,
                    "summary": comment.article.summary,
                    "createdAt": comment.article.created_at,
                    "coverImage": comment.article.cover_image,
                }

            comments_data.append(comment_info)

        metadata = {
            "pagination": {
                "offset": (page - 1) * limit if (page and limit) else None,
                "limit": limit,
                "previousOffset": (page - 2) * limit if page > 1 else None,
                "nextOffset": page * limit if comments else None,
                "currentPage": page if page else None,
                "totalCount": query.count(),
            },
            "sortedBy": {
                "name": sort_by,
                "order": sort_order,
            },
        }

        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Get all comments route",
            "data": {
                "comments": comments_data,
                "metadata": metadata,
            },
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


@comments_bp.route("/comments", methods=["POST"])
@jwt_required()
def create_comment():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), HTTPStatus.BAD_REQUEST

    content = data.get("content")
    author_id = data.get("author_id")
    article_id = data.get("article_id")

    if not all([content, author_id, article_id]):
        return jsonify({"message": "Missing required fields"}), HTTPStatus.BAD_REQUEST

    comment = Comment(
        content=content,
        author_id=author_id,
        article_id=article_id,
    )
    db.session.add(comment)
    db.session.commit()

    response_data = {
        "statusCode": HTTPStatus.CREATED,
        "message": "Create comment successful",
        "data": {
            "comment": {
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "author": {
                    "id": comment.author.id,
                    "email": comment.author.email,
                    "display_name": comment.author.display_name,
                    "avatar_image": comment.author.avatar_image,
                },
            }
        },
    }
    return jsonify(response_data), HTTPStatus.CREATED


@comments_bp.route("/comments/<int:comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), HTTPStatus.BAD_REQUEST

    content = data.get("content")
    if not content:
        return jsonify({"message": "No content provided"}), HTTPStatus.BAD_REQUEST

    comment.content = content
    db.session.commit()

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "Comment updated successfully",
        "data": {
            "comment": {
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "author": {
                    "id": comment.author.id,
                    "email": comment.author.email,
                    "display_name": comment.author.display_name,
                    "avatar_image": comment.author.avatar_image,
                },
            }
        },
    }
    return jsonify(response_data), HTTPStatus.OK


@comments_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted successfully"}), HTTPStatus.OK

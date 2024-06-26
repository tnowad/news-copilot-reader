from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.article import Article
from app.models.comment import Comment
from app.models.role import RoleEnum
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
        parent_id = request.args.get("parentId", type=int)

        query = Comment.query
        query = query.filter(Comment.deleted_at.is_(None))

        if parent_id:
            query = query.filter(Comment.parent_id == parent_id)  # type: ignore

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
                "parentId": comment.parent_id,
                "createdAt": comment.created_at,
                "updatedAt": comment.updated_at,
            }

            if style == "full":
                comment_info["deletedAt"] = comment.deleted_at

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
            "filters": {
                "articleId": article_id,
                "userId": user_id,
                "parentId": parent_id,
                "search": search,
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


@comments_bp.route("/comments/<int:comment_id>", methods=["GET"])
def get_comment(comment_id):
    try:
        if comment_id is None:
            return (
                jsonify(
                    {
                        "statusCode": HTTPStatus.BAD_REQUEST,
                        "message": "Comment ID is required",
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        comment = Comment.query.get(comment_id)
        if comment is None:
            return (
                jsonify(
                    {
                        "statusCode": HTTPStatus.NOT_FOUND,
                        "message": "Comment not found",
                        "error": f"Comment with id {comment_id} not found",
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": f"Get comment with id {comment_id} route",
            "data": {
                "comment": {
                    "id": comment.id,
                    "content": comment.content,
                    "parentId": comment.parent_id,
                    "createdAt": comment.created_at,
                    "updatedAt": comment.updated_at,
                }
            },
        }

        style_param = request.args.get("style")
        includes_param = request.args.getlist("includes")

        if style_param == "full":
            response_data["data"]["comment"]["deletedAt"] = comment.deleted_at

        if "author" in includes_param and comment.author:
            response_data["data"]["comment"]["author"] = {
                "id": comment.author.id,
                "email": comment.author.email,
                "displayName": comment.author.display_name,
                "avatarImage": comment.author.avatar_image,
            }

        if "article" in includes_param and comment.article:
            response_data["data"]["comment"]["article"] = {
                "id": comment.article.id,
                "title": comment.article.title,
                "summary": comment.article.summary,
                "createdAt": comment.article.created_at,
                "coverImage": comment.article.cover_image,
            }

        if "childComments" in includes_param and comment.child_comments:
            child_comments_data = []
            for child_comment in comment.child_comments:
                child_comment_info = {
                    "id": child_comment.id,
                    "content": child_comment.content,
                    "parentId": child_comment.parent_id,
                    "createdAt": child_comment.created_at,
                    "updatedAt": child_comment.updated_at,
                }

                if style_param == "full":
                    child_comment_info["deletedAt"] = child_comment.deleted_at

                if "author" in includes_param and child_comment.author:
                    child_comment_info["author"] = {
                        "id": child_comment.author.id,
                        "email": child_comment.author.email,
                        "displayName": child_comment.author.display_name,
                        "avatarImage": child_comment.author.avatar_image,
                    }

                if "article" in includes_param and child_comment.article:
                    child_comment_info["article"] = {
                        "id": child_comment.article.id,
                        "title": child_comment.article.title,
                        "summary": child_comment.article.summary,
                        "createdAt": child_comment.article.created_at,
                        "coverImage": child_comment.article.cover_image,
                    }

                child_comments_data.append(child_comment_info)

            response_data["data"]["comment"]["childComments"] = child_comments_data

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
    author_id = data.get("authorId")
    article_id = data.get("articleId")

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
                "createdAt": comment.created_at,
                "updatedAt": comment.updated_at,
                "author": {
                    "id": comment.author.id,
                    "email": comment.author.email,
                    "displayName": comment.author.display_name,
                    "avatarImage": comment.author.avatar_image,
                },
            }
        },
    }
    return jsonify(response_data), HTTPStatus.CREATED


@comments_bp.route("/comments/<int:comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)

        if not comment:
            return (
                jsonify(
                    {
                        "statusCode": HTTPStatus.NOT_FOUND,
                        "message": "Cannot update comment",
                        "error": f"Comment with id {comment_id} not found",
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        current_user = User.query.filter_by(email=get_jwt_identity()).first()

        if not current_user or (
            not any(role.name == RoleEnum.ADMIN for role in current_user.roles)
            and current_user.id != comment.author_id
        ):
            return (
                jsonify(
                    {
                        "statusCode": HTTPStatus.UNAUTHORIZED,
                        "message": "You are not authorized to update this comment",
                        "error": "Unauthorized",
                    }
                ),
                HTTPStatus.UNAUTHORIZED,
            )

        data = request.get_json()
        content = data.get("content")

        if content:
            comment.content = content
            comment.updated_at = datetime.now()

        db.session.commit()

        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.OK,
                    "message": "Comment updated successfully",
                    "data": {
                        "id": comment.id,
                        "content": comment.content,
                        "createdAt": comment.created_at,
                        "updatedAt": comment.updated_at,
                    },
                }
            ),
            HTTPStatus.OK,
        )

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


@comments_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)

        if not comment:
            return (
                jsonify(
                    {
                        "statusCode": HTTPStatus.NOT_FOUND,
                        "message": "Cannot delete comment",
                        "error": f"Comment with id {comment_id} not found",
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        current_user = User.query.filter_by(email=get_jwt_identity()).first()

        if not current_user or (
            not any(role.name == RoleEnum.ADMIN for role in current_user.roles)
            and current_user.id == comment.author_id
        ):
            return (
                jsonify(
                    {
                        "statusCode": HTTPStatus.UNAUTHORIZED,
                        "message": "You are not authorized to delete this comment",
                        "error": "Unauthorized",
                    }
                ),
                HTTPStatus.UNAUTHORIZED,
            )

        comment.deleted_at = datetime.now()
        db.session.commit()

        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.OK,
                    "message": "Comment deleted successfully",
                }
            ),
            HTTPStatus.OK,
        )

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

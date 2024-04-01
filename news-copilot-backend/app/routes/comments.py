from flask import Blueprint, jsonify, request

from app.models.comment import Comment
from app.extensions import db
from http import HTTPStatus
from flask_jwt_extended import jwt_required

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/comments", methods=["GET"])
def get_comments():
    comments = Comment.query.all()

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "Get all comments successful",
        "data": {
            "comments": [
                {
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
                for comment in comments
            ]
        },
    }

    return jsonify(response_data), HTTPStatus.OK


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

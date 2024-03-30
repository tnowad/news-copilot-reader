from flask import Blueprint, jsonify

from app.models.comment import Comment
from http import HTTPStatus

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

from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.article import Article
from app.models.bookmark import Bookmark
from app.models.user import User

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
    user_id = get_jwt_identity()

    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()

    bookmark_data = []
    for bookmark in bookmarks:
        bookmark_info = {
            "id": bookmark.id,
            "article_id": bookmark.article_id,
            "created_at": bookmark.created_at.isoformat(),
        }
        bookmark_data.append(bookmark_info)

    return jsonify({"bookmarks": bookmark_data}), HTTPStatus.OK


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

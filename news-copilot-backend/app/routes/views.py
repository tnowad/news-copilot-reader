from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.article import Article
from app.models.user import User
from app.models.view import View

views_bp = Blueprint("views", __name__)


@views_bp.route("/articles/<int:article_id>/mark-viewed", methods=["POST"])
@jwt_required()
def mark_article_viewed(article_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()

    article = Article.query.get(article_id)
    if not article:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": "Article not found",
                }
            ),
            HTTPStatus.NOT_FOUND,
        )

    existing_view = View.query.filter_by(
        article_id=article_id, user_id=current_user.id
    ).first()

    if existing_view:
        existing_view.viewed_at = datetime.now()
    else:
        new_view = View(
            article_id=article_id, user_id=current_user.id, viewed_at=datetime.now()
        )
        db.session.add(new_view)

    db.session.commit()

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "Article marked as viewed successfully",
        "data": {
            "view": {
                "articleId": article_id,
                "userId": current_user.id,
                "viewedAt": datetime.now().isoformat(),
            }
        },
    }

    return jsonify(response_data), HTTPStatus.OK

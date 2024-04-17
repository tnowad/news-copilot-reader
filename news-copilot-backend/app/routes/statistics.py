from http import HTTPStatus
from flask import Blueprint, jsonify

from app.models.article import Article
from app.models.view import View
from app.models.comment import Comment

statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.route("/statistics/articles", methods=["GET"])
def articles_statistics():
    total_articles = Article.query.count()
    total_views = View.query.count()
    total_comments = Comment.query.count()

    statistics = {
        "totalArticles": total_articles,
        "totalViews": total_views,
        "totalComments": total_comments,
    }

    return jsonify(
        {
            "statusCode": HTTPStatus.OK,
            "data": statistics,
            "message": "Statistics retrieved successfully",
        }
    )

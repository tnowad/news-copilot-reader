from http import HTTPStatus
from flask import Blueprint, jsonify
from sqlalchemy import func

from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.view import View
from app.models.comment import Comment

from app.extensions import db

statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.route("/statistics/all", methods=["GET"])
def get_all_statistics():
    total_articles = Article.query.count()
    total_views = View.query.count()
    total_comments = Comment.query.count()
    total_user = User.query.count()
    total_category = Category.query.count()
    statistics = {
        "totalUser": total_user,
        "totalArticles": total_articles,
        "totalViews": total_views,
        "totalComments": total_comments,
        "totalCategories": total_category,
    }

    return jsonify(
        {
            "statusCode": HTTPStatus.OK,
            "data": statistics,
            "message": "Statistics retrieved successfully",
        }
    )


@statistics_bp.route("/statistics/categories-articles", methods=["GET"])
def category_article_count():
    category_counts = (
        db.session.query(Category.title, func.count(Article.id))
        .outerjoin(Article.categories)
        .group_by(Category.title)
        .all()
    )

    categories = []
    counts = []
    for category, count in category_counts:
        categories.append(category)
        counts.append(count)

    apex_options = {
        "chart": {"type": "bar"},
        "series": [{"name": "Articles", "data": counts}],
        "xaxis": {"categories": categories},
        "title": {"text": "Articles per Category"},
    }

    return jsonify(
        {
            "statusCode": HTTPStatus.OK,
            "data": apex_options,
            "message": "Category article counts retrieved successfully",
        }
    )

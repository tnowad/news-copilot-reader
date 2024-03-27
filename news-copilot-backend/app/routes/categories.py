from http import HTTPStatus
from flask import Blueprint, jsonify

from app.models.category import Category

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "data": {
                    "categories": [
                        {
                            "id": category.id,
                            "slug": category.slug,
                            "title": category.title,
                        }
                        for category in categories
                    ]
                },
                "message": "Get all categories successful",
            }
        ),
        HTTPStatus.OK,
    )


@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    return jsonify({"message": f"Get category with id {category_id} route"})

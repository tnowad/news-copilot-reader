from http import HTTPStatus
from flask import Blueprint, jsonify, request

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
                            "description": category.description,
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
    category = Category.query.get(category_id)
    if not category:
        return jsonify(
            {
                "status": HTTPStatus.NOT_FOUND,
                "message": "{category_id} not found",
                "error": "{category_id} not found",
            }
        )
    response_data = {
        "data": {
            "category": {
                "id": category.id,
                "slug": category.slug,
                "title": category.title,
            }
        },
        "status": HTTPStatus.OK,
        "message": f"Get category by id {category.id} successful",
    }

    style_param = request.args.get("style")

    if style_param == "full":
        response_data["data"]["category"]["description"] = category.description

    include_params = request.args.getlist("include")

    if "author" in include_params:
        response_data["data"]["category"]["author"] = {
            "id": category.author.id,
            "email": category.author.email,
            "displayName": category.author.display_name,
            "avatarImage": category.author.avatar_image,
        }

    return jsonify(response_data), HTTPStatus.OK

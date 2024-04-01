from http import HTTPStatus
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.decorators.authorization import role_required
from app.models.category import Category
from app.models.role import RoleEnum
from app.extensions import db
from app.models.article import Article

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
                "statusCode": HTTPStatus.NOT_FOUND,
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
        "statusCode": HTTPStatus.OK,
        "message": f"Get category by id {category.id} successful",
    }

    style_param = request.args.get("style")
    include_params = request.args.getlist("include")

    if style_param == "full":
        response_data["data"]["category"]["description"] = category.description

    if "author" in include_params:
        response_data["data"]["category"]["author"] = {
            "id": category.author.id,
            "email": category.author.email,
            "displayName": category.author.display_name,
            "avatarImage": category.author.avatar_image,
        }

    return jsonify(response_data), HTTPStatus.OK


# TODO: dont handle role in create category
@categories_bp.route("/categories", methods=["POST"])
@jwt_required()
@role_required([RoleEnum.ADMIN])
def create_category():
    data = request.get_json()
    slug = data.get("slug")
    title = data.get("title")
    description = data.get("description")
    category = Category(title=title, slug=slug, description=description)
    db.session.add(category)
    db.session.commit()
    response_data = {
        "statusCode": HTTPStatus.CREATED,
        "message": "Category created successfully",
        "data": {
            "id": category.id,
            "title": category.title,
            "slug": category.slug,
            "description": category.description,
        },
    }
    return jsonify(response_data), HTTPStatus.CREATED


@categories_bp.route("/categories/<int:category_id>", methods=["PUT"])
@jwt_required()
@role_required([RoleEnum.ADMIN])
def update_category(category_id):
    data = request.get_json()
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), HTTPStatus.NOT_FOUND
    category.title = data.get("title", category.title)
    category.slug = data.get("slug", category.slug)
    category.description = data.get("description", category.description)
    db.session.commit()
    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "Category updated successfully",
        "data": {
            "id": category.id,
            "title": category.title,
            "slug": category.slug,
            "description": category.description,
        },
    }
    return jsonify(response_data), HTTPStatus.OK


@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@jwt_required()
@role_required([RoleEnum.ADMIN])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), HTTPStatus.NOT_FOUND
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted successfully"}), HTTPStatus.OK

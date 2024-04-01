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
    try:
        page = request.args.get("page", type=int) or 1
        limit = request.args.get("limit", type=int) or 10
        sort_by = request.args.get("sortBy", type=str)
        sort_order = request.args.get("sortOrder", type=str)
        style = request.args.get("style", type=str)
        includes = request.args.getlist("includes", type=str)
        search = request.args.get("search", type=str)

        query = Category.query

        if search:
            query = query.filter(Category.title.ilike(f"%{search}%"))  # type: ignore

        if sort_by and sort_order:
            if sort_by == "title":
                query = query.order_by(
                    Category.title.asc()  # type: ignore
                    if sort_order == "asc"
                    else Category.title.desc()  # type: ignore
                )
            elif sort_by == "id":
                query = query.order_by(
                    Category.id.asc() if sort_order == "asc" else Category.id.desc()
                )

        if page and limit:
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

        categories = query.all()

        categories_data = []
        for category in categories:
            category_info = {
                "id": category.id,
                "title": category.title,
                "slug": category.slug,
                "description": category.description,
            }

            if style == "full":
                category_info["articles"] = [
                    {
                        "id": article.id,
                        "title": article.title,
                        "summary": article.summary,
                        "createdAt": article.created_at,
                        "coverImage": article.cover_image,
                    }
                    for article in category.articles
                ]

            if "articles" in includes:
                category_info["articles"] = [
                    {
                        "id": article.id,
                        "title": article.title,
                    }
                    for article in category.articles
                ]

            categories_data.append(category_info)

        metadata = {
            "pagination": {
                "offset": (page - 1) * limit if (page and limit) else None,
                "limit": limit,
                "previousOffset": (page - 2) * limit if page > 1 else None,
                "nextOffset": page * limit if categories else None,
                "currentPage": page if page else None,
                "totalCount": query.count(),
            },
            "sortedBy": {
                "name": sort_by,
                "order": sort_order,
            },
            "style": style,
        }

        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Get all categories route",
            "data": {
                "categories": categories_data,
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

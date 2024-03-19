from flask import Blueprint, jsonify

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categories", methods=["GET"])
def get_categories():
    return jsonify({"message": "Get all categories route"})


@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    return jsonify({"message": f"Get category with id {category_id} route"})

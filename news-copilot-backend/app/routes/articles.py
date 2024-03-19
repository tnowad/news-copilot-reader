from flask import Blueprint, jsonify

articles_bp = Blueprint("articles", __name__)


@articles_bp.route("/articles", methods=["GET"])
def get_articles():
    return jsonify({"message": "Get all articles route"})


@articles_bp.route("/articles/<int:article_id>", methods=["GET"])
def get_article(article_id):
    return jsonify({"message": f"Get article with id {article_id} route"})

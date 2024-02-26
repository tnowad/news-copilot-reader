from flask import Blueprint, jsonify

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    return jsonify({"message": "Login route"})


@auth_bp.route("/logout", methods=["GET"])
def logout():
    return jsonify({"message": "Logout route"})

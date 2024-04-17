from datetime import datetime
from http import HTTPStatus
from typing import List

from flask import Blueprint, jsonify, request
from app.models.report import Report

report_bp = Blueprint("report", __name__)


@report_bp.route("/reports", methods=["POST"])
def create_report():
    data = request.get_json()
    id = data.get("id")
    content = data.get("content")
    object_id = data.get("object_id")
    object_type = data.get("object_type")
    report = Report(id, content, object_type, object_id)
    print(report)
    return (
        jsonify(
            {
                "statusCode": HTTPStatus.ACCEPTED,
                "message": "Internal Server Error",
            }
        ),
        HTTPStatus.ACCEPTED,
    )

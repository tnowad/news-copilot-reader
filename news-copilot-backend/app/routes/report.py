from datetime import datetime
from http import HTTPStatus
from typing import List


from app.extensions import db
from flask import Blueprint, jsonify, request
from app.models.report import Report

report_bp = Blueprint("report", __name__)


@report_bp.route("/reports", methods=["POST"])
def create_report():
    data = request.get_json()
    content = data.get("content")
    object_id = data.get("objectId")
    object_type = data.get("objectType")
    created_at = datetime.now()

    report = Report(
        content,
        object_type,
        object_id,
        created_at,
    )

    # db.session.query(Report).delete()
    # db.session.commit()

    db.session.add(report)
    db.session.commit()
    """reports = Report.query.all()
    print("Report Data:")
    print("ID\t| Object ID\t| Object Type\t| Created At\t\t\t| Content")
    print("-" * 80)
    for report in reports:
        print(
            f"{report.id}\t| {report.object_id}\t\t| {report.object_type}\t\t| {report.created_at}\t| {report.content}"
        )"""
    return (
        jsonify(
            {
                "id": report.id,
                "object_id": report.object_id,
                "object_type": report.object_type,
                "created": report.created_at,
                "content": report.content,
                "statusCode": HTTPStatus.ACCEPTED,
                "message": "Report was successfully created",
            }
        ),
        HTTPStatus.ACCEPTED,
    )

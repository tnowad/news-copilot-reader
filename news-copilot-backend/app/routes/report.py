from datetime import datetime
from http import HTTPStatus
from typing import List


from app.extensions import db
from flask import Blueprint, jsonify, request
from app.models.report import Report

report_bp = Blueprint("report", __name__)


@report_bp.route("/reports", methods=["GET"])
def get_report():
    try:
        page = request.args.get("page", type=int) or 1
        limit = request.args.get("limit", type=int) or 10
        sort_by = request.args.get("sortBy", type=str)
        sort_order = request.args.get("sortOrder", type=str)
        style = request.args.get("style", type=str)
        search = request.args.get("search", type=str)

        query = Report.query

        if search:
            query = query.filter(Report.title.ilike(f"%{search}%"))  # type: ignore

        if sort_by and sort_order:
            if sort_by == "id":
                query = query.order_by(
                    Report.id.asc() if sort_order == "asc" else Report.id.desc()
                )
            if sort_by == "created_at":
                query = query.order_by(
                    Report.created_at.asc()
                    if sort_order == "asc"
                    else Report.created_at.desc()
                )

        if page and limit:
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

        reports = query.all()

        reports_data = []
        for report in reports:
            report_info = {
                "id": report.id,
                "content": report.content,
                "objectType": report.object_type,
                "objectId": report.object_id,
            }
            reports_data.append(report_info)

        metadata = {
            "pagination": {
                "offset": (page - 1) * limit if (page and limit) else None,
                "limit": limit,
                "previousOffset": (page - 2) * limit if page > 1 else None,
                "nextOffset": page * limit if reports else None,
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
            "message": "Get all report route",
            "data": {
                "reports": reports_data,
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


@report_bp.route("/reports", methods=["POST"])
def create_report():
    try:
        data = request.get_json()
        content = data.get("content")
        object_id = data.get("objectId")
        object_type = data.get("objectType")
        created_at = datetime.now()

        report = Report(
            content,
            object_id,
            object_type,
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


@report_bp.route("/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "message": "Report deleted successfully",
            }
        ),
        HTTPStatus.OK,
    )


@report_bp.route("/reports/<int:report_id>", methods=["PUT"])
def update_report(report_id):
    report = Report.query.get_or_404(report_id)
    data = request.get_json()
    content = data.get("content")

    report.content = content
    db.session.commit()

    response_data = {
        "id": report.id,
        "object_id": report.object_id,
        "object_type": report.object_type,
        "created": report.created_at,
        "content": report.content,
        "message": "Report updated successfully",
    }

    response = {
        "statusCode": HTTPStatus.OK,
        "message": "Report updated successfully",
        "data": response_data,
    }

    return jsonify(response), HTTPStatus.OK


@report_bp.route("/reports/<int:report_id>", methods=["GET"])
def get_report_by_id(report_id):
    try:
        report = Report.query.get_or_404(report_id)

        report_data = {
            "id": report.id,
            "content": report.content,
            "objectType": report.object_type,
            "objectId": report.object_id,
        }

        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Get report by ID",
            "data": report_data,
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

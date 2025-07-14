from datetime import datetime
from http import HTTPStatus
import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.services.report_service import ReportService
from app.utils.response_helper import APIResponse
from app.decorators.authorization import authorize_roles

logger = logging.getLogger(__name__)
report_service = ReportService()

report_bp = Blueprint("report", __name__)


@report_bp.route("/reports", methods=["GET"])
@jwt_required()
@authorize_roles(['admin', 'moderator'])
def get_reports():
    """
    Get all reports with optional filtering and pagination
    """
    try:
        # Extract query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 100)
        sort_by = request.args.get("sortBy", "created_at")
        sort_order = request.args.get("sortOrder", "desc")
        report_type = request.args.get("type")
        status = request.args.get("status")
        reported_by = request.args.get("reported_by", type=int)
        search = request.args.get("search")

        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return APIResponse.error("User not found", HTTPStatus.NOT_FOUND)

        # Get reports using service
        result = report_service.get_reports_with_filters(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            report_type=report_type,
            status=status,
            reported_by=reported_by,
            current_user=current_user,
            search=search
        )

        logger.info(f"Retrieved {len(result['reports'])} reports for user {current_user_id}")
        return APIResponse.success("Reports retrieved successfully", result)

    except Exception as e:
        logger.error(f"Error retrieving reports: {str(e)}")
        return APIResponse.error("Error retrieving reports", HTTPStatus.INTERNAL_SERVER_ERROR)


@report_bp.route("/reports", methods=["POST"])
@jwt_required()
def create_report():
    """
    Create a new report
    """
    try:
        data = request.get_json()
        if not data:
            return APIResponse.error("No data provided", HTTPStatus.BAD_REQUEST)

        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return APIResponse.error("User not found", HTTPStatus.NOT_FOUND)

        # Extract required fields
        content = data.get("content")
        object_type = data.get("objectType")
        object_id = data.get("objectId")

        if not all([content, object_type, object_id]):
            return APIResponse.error("Missing required fields: content, objectType, objectId", HTTPStatus.BAD_REQUEST)

        # Create report using service
        report_data = {
            'content': content,
            'object_type': object_type,
            'object_id': object_id,
            'reported_by': current_user_id,
            'status': 'pending'
        }

        report = report_service.create_report(report_data, current_user)
        
        logger.info(f"Report {report['id']} created by user {current_user_id}")
        return APIResponse.success("Report created successfully", report, HTTPStatus.CREATED)

    except ValueError as e:
        logger.warning(f"Invalid report data: {str(e)}")
        return APIResponse.error(str(e), HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating report: {str(e)}")
        return APIResponse.error("Error creating report", HTTPStatus.INTERNAL_SERVER_ERROR)


@report_bp.route("/reports/<int:report_id>", methods=["GET"])
@jwt_required()
@authorize_roles(['admin', 'moderator'])
def get_report_by_id(report_id):
    """
    Get a specific report by ID
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return APIResponse.error("User not found", HTTPStatus.NOT_FOUND)

        # Get report using service
        report = report_service.get_report_by_id(report_id, current_user)
        
        if not report:
            return APIResponse.error("Report not found", HTTPStatus.NOT_FOUND)

        logger.info(f"Report {report_id} retrieved by user {current_user_id}")
        return APIResponse.success("Report retrieved successfully", report)

    except Exception as e:
        logger.error(f"Error retrieving report {report_id}: {str(e)}")
        return APIResponse.error("Error retrieving report", HTTPStatus.INTERNAL_SERVER_ERROR)


@report_bp.route("/reports/<int:report_id>", methods=["PUT"])
@jwt_required()
@authorize_roles(['admin', 'moderator'])
def update_report(report_id):
    """
    Update a report (typically to change status or add review)
    """
    try:
        data = request.get_json()
        if not data:
            return APIResponse.error("No data provided", HTTPStatus.BAD_REQUEST)

        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return APIResponse.error("User not found", HTTPStatus.NOT_FOUND)

        # Update report using service
        updated_report = report_service.update_report(report_id, data, current_user)
        
        if not updated_report:
            return APIResponse.error("Report not found", HTTPStatus.NOT_FOUND)

        logger.info(f"Report {report_id} updated by user {current_user_id}")
        return APIResponse.success("Report updated successfully", updated_report)

    except ValueError as e:
        logger.warning(f"Invalid update data for report {report_id}: {str(e)}")
        return APIResponse.error(str(e), HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating report {report_id}: {str(e)}")
        return APIResponse.error("Error updating report", HTTPStatus.INTERNAL_SERVER_ERROR)


@report_bp.route("/reports/<int:report_id>", methods=["DELETE"])
@jwt_required()
@authorize_roles(['admin'])
def delete_report(report_id):
    """
    Delete a report (admin only)
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return APIResponse.error("User not found", HTTPStatus.NOT_FOUND)

        # Delete report using service
        success = report_service.delete_report(report_id, current_user)
        
        if not success:
            return APIResponse.error("Report not found", HTTPStatus.NOT_FOUND)

        logger.info(f"Report {report_id} deleted by user {current_user_id}")
        return APIResponse.success("Report deleted successfully")

    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {str(e)}")
        return APIResponse.error("Error deleting report", HTTPStatus.INTERNAL_SERVER_ERROR)


@report_bp.route("/reports/by-object", methods=["GET"])
@jwt_required()
@authorize_roles(['admin', 'moderator'])
def get_reports_by_object():
    """
    Get reports for a specific object (article, comment, user)
    """
    try:
        object_type = request.args.get('type')
        object_id = request.args.get('id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)

        if not object_type or not object_id:
            return APIResponse.error("Missing required parameters: type and id", HTTPStatus.BAD_REQUEST)

        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return APIResponse.error("User not found", HTTPStatus.NOT_FOUND)

        # Get reports using service
        result = report_service.get_reports_by_object(
            object_type=object_type,
            object_id=object_id,
            page=page,
            per_page=per_page,
            current_user=current_user
        )

        logger.info(f"Retrieved {len(result['reports'])} reports for {object_type} {object_id}")
        return APIResponse.success("Reports retrieved successfully", result)

    except ValueError as e:
        logger.warning(f"Invalid object type or ID: {str(e)}")
        return APIResponse.error(str(e), HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error retrieving reports by object: {str(e)}")
        return APIResponse.error("Error retrieving reports", HTTPStatus.INTERNAL_SERVER_ERROR)


@report_bp.route("/reports/statistics", methods=["GET"])
@jwt_required()
@authorize_roles(['admin', 'moderator'])
def get_report_statistics():
    """
    Get report statistics (counts by status, type, etc.)
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return APIResponse.error("User not found", HTTPStatus.NOT_FOUND)

        # Get statistics using service
        stats = report_service.get_report_statistics(current_user)

        logger.info(f"Report statistics retrieved by user {current_user_id}")
        return APIResponse.success("Statistics retrieved successfully", stats)

    except Exception as e:
        logger.error(f"Error retrieving report statistics: {str(e)}")
        return APIResponse.error("Error retrieving statistics", HTTPStatus.INTERNAL_SERVER_ERROR)

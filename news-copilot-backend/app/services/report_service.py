from typing import Dict, Any, Optional, List
from http import HTTPStatus
from datetime import datetime
import logging

from app.services.base_service import BaseService
from app.models.report import Report
from app.extensions import db, cache

logger = logging.getLogger(__name__)


class ReportService(BaseService):
    """Service for managing reports"""
    
    def __init__(self):
        super().__init__(Report)
    
    def get_reports_with_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get reports with advanced filtering and pagination"""
        try:
            page = filters.get('page', 1)
            limit = filters.get('limit', 10)
            sort_by = filters.get('sort_by')
            sort_order = filters.get('sort_order')
            style = filters.get('style')
            search = filters.get('search')

            # Build cache key
            cache_key = f"reports:{hash(str(sorted(filters.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info("Returning cached reports")
                return cached_result

            # Build query
            query = Report.query

            # Apply search filter
            if search:
                query = query.filter(Report.title.ilike(f"%{search}%"))

            # Apply sorting
            if sort_by and sort_order:
                if sort_by == "id":
                    query = query.order_by(
                        Report.id.asc() if sort_order == "asc" else Report.id.desc()
                    )
                elif sort_by == "created_at":
                    query = query.order_by(
                        Report.created_at.asc() if sort_order == "asc" else Report.created_at.desc()
                    )

            # Get total count before pagination
            total_count = query.count()

            # Apply pagination
            if page and limit:
                offset = (page - 1) * limit
                query = query.offset(offset).limit(limit)

            reports = query.all()

            # Serialize reports
            reports_data = []
            for report in reports:
                report_info = self._serialize_report(report, style)
                reports_data.append(report_info)

            # Build metadata
            metadata = self._build_pagination_metadata(page, limit, total_count, sort_by, sort_order, style)

            result = self._format_response(
                HTTPStatus.OK,
                "Reports retrieved successfully",
                {"reports": reports_data, "metadata": metadata}
            )

            # Cache the result for 5 minutes
            cache.set(cache_key, result, timeout=300)

            logger.info(f"Retrieved {len(reports_data)} reports with filters: {filters}")
            return result

        except Exception as e:
            logger.error(f"Error retrieving reports: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve reports",
                str(e)
            )

    def get_report_by_id(self, report_id: int) -> Dict[str, Any]:
        """Get a specific report by ID"""
        try:
            report = Report.query.get(report_id)
            
            if not report:
                logger.warning(f"Report {report_id} not found")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Report not found",
                    f"Report with id {report_id} not found"
                )

            report_data = self._serialize_report(report, "full")

            logger.info(f"Retrieved report {report_id}")
            return self._format_response(
                HTTPStatus.OK,
                f"Report {report_id} retrieved successfully",
                report_data
            )

        except Exception as e:
            logger.error(f"Error retrieving report {report_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve report",
                str(e)
            )

    def create_report(self, data: Dict[str, Any], current_user_email: str = None) -> Dict[str, Any]:
        """Create a new report"""
        try:
            content = data.get("content")
            object_id = data.get("objectId")
            object_type = data.get("objectType")

            if not all([content, object_id, object_type]):
                logger.warning("Missing required fields for report creation")
                return self._format_error_response(
                    HTTPStatus.BAD_REQUEST,
                    "Missing required fields: content, objectId, objectType"
                )

            # Validate object_type
            valid_object_types = ['article', 'comment', 'user']  # Add more as needed
            if object_type not in valid_object_types:
                logger.warning(f"Invalid object_type: {object_type}")
                return self._format_error_response(
                    HTTPStatus.BAD_REQUEST,
                    f"Invalid object_type. Must be one of: {', '.join(valid_object_types)}"
                )

            report = Report(
                content=content,
                object_id=object_id,
                object_type=object_type,
                created_at=datetime.now()
            )

            db.session.add(report)
            db.session.commit()

            # Clear reports cache
            cache.delete_many('reports:*')

            report_data = self._serialize_report(report, "full")

            logger.info(f"Report created successfully by user {current_user_email or 'anonymous'}")
            return self._format_response(
                HTTPStatus.CREATED,
                "Report created successfully",
                report_data
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating report: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to create report",
                str(e)
            )

    def update_report(self, report_id: int, data: Dict[str, Any], current_user_email: str = None) -> Dict[str, Any]:
        """Update an existing report"""
        try:
            report = Report.query.get(report_id)

            if not report:
                logger.warning(f"Report {report_id} not found for update")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Report not found",
                    f"Report with id {report_id} not found"
                )

            content = data.get("content")
            if content:
                report.content = content
                report.updated_at = datetime.now()

            db.session.commit()

            # Clear reports cache
            cache.delete_many('reports:*')

            report_data = self._serialize_report(report, "full")

            logger.info(f"Report {report_id} updated successfully by user {current_user_email or 'anonymous'}")
            return self._format_response(
                HTTPStatus.OK,
                "Report updated successfully",
                report_data
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating report {report_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to update report",
                str(e)
            )

    def delete_report(self, report_id: int, current_user_email: str = None) -> Dict[str, Any]:
        """Delete a report"""
        try:
            report = Report.query.get(report_id)

            if not report:
                logger.warning(f"Report {report_id} not found for deletion")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Report not found",
                    f"Report with id {report_id} not found"
                )

            db.session.delete(report)
            db.session.commit()

            # Clear reports cache
            cache.delete_many('reports:*')

            logger.info(f"Report {report_id} deleted successfully by user {current_user_email or 'anonymous'}")
            return self._format_response(
                HTTPStatus.OK,
                "Report deleted successfully"
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting report {report_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to delete report",
                str(e)
            )

    def get_reports_by_object(self, object_type: str, object_id: int, limit: int = 10) -> Dict[str, Any]:
        """Get reports for a specific object"""
        try:
            # Build cache key
            cache_key = f"reports_by_object:{object_type}:{object_id}:{limit}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached reports for {object_type}:{object_id}")
                return cached_result

            reports = Report.query.filter_by(
                object_type=object_type,
                object_id=object_id
            ).limit(limit).all()

            reports_data = []
            for report in reports:
                report_info = self._serialize_report(report)
                reports_data.append(report_info)

            result = self._format_response(
                HTTPStatus.OK,
                f"Reports for {object_type} {object_id} retrieved successfully",
                {"reports": reports_data, "total": len(reports_data)}
            )

            # Cache the result for 10 minutes
            cache.set(cache_key, result, timeout=600)

            logger.info(f"Retrieved {len(reports_data)} reports for {object_type}:{object_id}")
            return result

        except Exception as e:
            logger.error(f"Error retrieving reports for {object_type}:{object_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve object reports",
                str(e)
            )

    def get_report_statistics(self) -> Dict[str, Any]:
        """Get report statistics"""
        try:
            # Build cache key
            cache_key = "report_statistics"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info("Returning cached report statistics")
                return cached_result

            total_reports = Report.query.count()
            
            # Reports by object type
            report_types = db.session.query(
                Report.object_type,
                db.func.count(Report.id).label('count')
            ).group_by(Report.object_type).all()

            type_stats = {obj_type: count for obj_type, count in report_types}

            # Recent reports (last 24 hours)
            from datetime import datetime, timedelta
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_reports = Report.query.filter(Report.created_at >= last_24h).count()

            statistics = {
                "total_reports": total_reports,
                "reports_by_type": type_stats,
                "recent_reports_24h": recent_reports,
                "generated_at": datetime.utcnow().isoformat()
            }

            result = self._format_response(
                HTTPStatus.OK,
                "Report statistics retrieved successfully",
                statistics
            )

            # Cache the result for 15 minutes
            cache.set(cache_key, result, timeout=900)

            logger.info("Retrieved report statistics")
            return result

        except Exception as e:
            logger.error(f"Error retrieving report statistics: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve report statistics",
                str(e)
            )

    def _serialize_report(self, report: Report, style: str = "compact") -> Dict[str, Any]:
        """Serialize report data"""
        report_info = {
            "id": report.id,
            "content": report.content,
            "objectType": report.object_type,
            "objectId": report.object_id,
            "createdAt": report.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        if style == "full":
            report_info.update({
                "updatedAt": (
                    report.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                    if hasattr(report, 'updated_at') and report.updated_at
                    else None
                )
            })

        return report_info

    def _build_pagination_metadata(self, page: int, limit: int, total_count: int, 
                                 sort_by: str, sort_order: str, style: str) -> Dict[str, Any]:
        """Build pagination metadata"""
        return {
            "pagination": {
                "offset": (page - 1) * limit if (page and limit) else None,
                "limit": limit,
                "previousOffset": (page - 2) * limit if page > 1 else None,
                "nextOffset": page * limit if total_count > page * limit else None,
                "currentPage": page if page else None,
                "totalCount": total_count,
            },
            "sortedBy": {
                "name": sort_by,
                "order": sort_order,
            },
            "style": style,
        }

    def _serialize(self, report: Report) -> Dict[str, Any]:
        """Basic report serialization"""
        return {
            "id": report.id,
            "content": report.content,
            "object_type": report.object_type,
            "object_id": report.object_id,
            "created_at": report.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        }

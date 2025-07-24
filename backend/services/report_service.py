from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.report import Report
from models.user import UserRole
from models.content import Content
from schemas.report import ReportCreate
from services.base import BaseService

class ReportService(BaseService[Report, ReportCreate, None]):
    def __init__(self, db: Session):
        super().__init__(Report, db)

    def create_report(self, report_data: ReportCreate, agency_id: int) -> Report:
        """Create new report for an agency"""
        # Ensure the agency_id matches the authenticated user
        if report_data.agency_id != agency_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create report for another agency"
            )

        # Verify content exists
        content = self.db.query(Content).filter(Content.id == report_data.content_id).first()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        db_report = Report(
            name=report_data.name,
            agency_id=agency_id,
            content_id=report_data.content_id
        )

        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)

        return db_report

    def get_agency_reports(self, agency_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all reports by a specific agency"""
        query = self.db.query(Report).filter(Report.agency_id == agency_id)
        return self.paginate_query(query, page, per_page)

    def get_all_reports(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all reports (admin only)"""
        query = self.db.query(Report)
        return self.paginate_query(query, page, per_page)

    def get_report_with_relations(self, report_id: int) -> Optional[Report]:
        """Get report with agency and content information"""
        return self.db.query(Report).filter(Report.id == report_id).first()

    def delete_report(self, report_id: int, user_id: int, user_role: UserRole) -> Report:
        """Delete report (agency can delete own, admin can delete any)"""
        report = self.get_or_404(report_id)

        # Check permissions
        if user_role != UserRole.ADMIN and report.agency_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this report"
            )

        self.db.delete(report)
        self.db.commit()
        return report

    def get_reports_by_content(self, content_id: int) -> List[Report]:
        """Get all reports for a specific content"""
        return self.db.query(Report).filter(Report.content_id == content_id).all()

    def paginate_query(self, query, page: int, per_page: int) -> Dict[str, Any]:
        """Paginate query results"""
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if total > 0 else 0
        }

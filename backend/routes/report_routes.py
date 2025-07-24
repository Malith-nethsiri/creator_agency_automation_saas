from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from services.report_service import ReportService
from schemas.report import ReportCreate, ReportOut, ReportOutWithRelations
from core.security import get_current_user, get_admin_user, require_roles
from core.utils import create_response
from models.user import UserRole

router = APIRouter()

@router.post("/", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["agency", "admin"]))
):
    """Create new report (Agency/Admin only)"""
    report_service = ReportService(db)

    try:
        report = report_service.create_report(report_data, current_user.id)
        return report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report"
        )

@router.get("/my-reports", response_model=dict)
async def get_my_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["agency", "admin"]))
):
    """Get current agency's reports"""
    report_service = ReportService(db)
    result = report_service.get_agency_reports(current_user.id, page, per_page)

    return create_response(
        success=True,
        message="Reports retrieved successfully",
        data=result
    )

@router.get("/", response_model=dict)
async def get_all_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get all reports (Admin only)"""
    report_service = ReportService(db)
    result = report_service.get_all_reports(page, per_page)

    return create_response(
        success=True,
        message="All reports retrieved successfully",
        data=result
    )

@router.get("/{report_id}", response_model=ReportOutWithRelations)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific report by ID"""
    report_service = ReportService(db)
    report = report_service.get_report_with_relations(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Check if user can access this report
    if (current_user.role != UserRole.ADMIN and
        report.agency_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this report"
        )

    return report

@router.delete("/{report_id}", response_model=dict)
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete report"""
    report_service = ReportService(db)

    try:
        deleted_report = report_service.delete_report(
            report_id, current_user.id, current_user.role
        )

        return create_response(
            success=True,
            message="Report deleted successfully",
            data={"deleted_report_id": deleted_report.id}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )

@router.get("/content/{content_id}", response_model=list[ReportOut])
async def get_reports_by_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all reports for specific content"""
    report_service = ReportService(db)
    reports = report_service.get_reports_by_content(content_id)

    return reports

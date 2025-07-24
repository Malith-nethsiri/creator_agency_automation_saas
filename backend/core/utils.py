from typing import Any, Dict, Optional, List
import uuid
from datetime import datetime
from sqlalchemy.orm import Query

def generate_uuid() -> str:
    """Generate a unique UUID string"""
    return str(uuid.uuid4())

def create_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """Create standardized API response"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    if data is not None:
        response["data"] = data
    return response

def paginate_query(
    query: Query,
    page: int = 1,
    per_page: int = 10
) -> Dict[str, Any]:
    """Paginate SQLAlchemy query"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total > 0 else 0
    }

class APIException(Exception):
    """Custom API exception"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

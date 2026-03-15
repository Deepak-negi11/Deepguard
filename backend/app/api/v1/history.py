from sqlalchemy import func, select
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, VerificationRequest
from app.schemas import HistoryItem, HistoryResponse

router = APIRouter()


@router.get("", response_model=HistoryResponse)
def get_history(limit: int = 20, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> HistoryResponse:
    query = (
        select(VerificationRequest)
        .where(VerificationRequest.user_id == user.id)
        .order_by(VerificationRequest.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = db.scalars(query).all()
    total = db.scalar(select(func.count()).select_from(VerificationRequest).where(VerificationRequest.user_id == user.id)) or 0
    items = [
        HistoryItem(
            request_id=row.id,
            type=row.request_type,
            status=row.status,
            verdict=row.result.verdict if row.result else None,
            confidence=row.result.confidence if row.result else None,
            created_at=row.created_at,
        )
        for row in rows
    ]
    return HistoryResponse(total=total, results=items)

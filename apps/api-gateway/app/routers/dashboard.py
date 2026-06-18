from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Project, ReviewJob, User
from app.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardSummary:
    project_ids = list(db.scalars(select(Project.id).where(Project.created_by == user.id)))
    reviews = list(
        db.scalars(select(ReviewJob).where(ReviewJob.project_id.in_(project_ids)).order_by(ReviewJob.created_at.desc()))
    )
    scorecards = [review.scorecard for review in reviews if review.scorecard]

    def avg(key: str) -> int:
        values = [int(score[key]) for score in scorecards if key in score]
        return round(sum(values) / len(values)) if values else 0

    trend_source = [review for review in reversed(reviews) if review.scorecard][-12:]
    security_trend = [
        {
            "label": review.created_at.strftime("%d %b"),
            "score": review.scorecard.get("security_score", 0),
        }
        for review in trend_source
    ]
    cost_trend = [
        {
            "label": review.created_at.strftime("%d %b"),
            "score": review.scorecard.get("cost_score", 0),
        }
        for review in trend_source
    ]
    recent: list[dict[str, Any]] = [
        {
            "id": review.id,
            "filename": review.original_filename,
            "status": review.status,
            "created_at": review.created_at.isoformat(),
            "score": review.scorecard.get("overall_score") if review.scorecard else None,
        }
        for review in reviews[:8]
    ]
    return DashboardSummary(
        total_reviews=len(reviews),
        average_score=avg("overall_score"),
        security_average=avg("security_score"),
        cost_average=avg("cost_score"),
        governance_average=avg("governance_score"),
        operations_average=avg("operations_score"),
        security_trend=security_trend,
        cost_trend=cost_trend,
        recent_reviews=recent,
    )


from fastapi import APIRouter, HTTPException

from models.scheduler import SchedulerRequest
from services.scheduler_pipeline import run_scheduler


router = APIRouter(
    prefix="/api/scheduler",
    tags=["Scheduler"]
)


@router.post("/")
def create_scheduler(request: SchedulerRequest):
    """
    Tạo lịch trình du lịch bằng Scheduler TV4.
    """

    try:
        result = run_scheduler(
            input_context=request.input_context,
            places=request.places,
            tv2_result=request.tv2_result,
            tv3_result=request.tv3_result
        )

        return result

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

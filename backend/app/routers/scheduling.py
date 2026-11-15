from __future__ import annotations

from fastapi import APIRouter

from generator.scheduling import solve_schedule_problem

from ..schemas.api import ScheduleRunRequest, ScheduleRunResponse
from ..services.dataset_service import get_dataset


router = APIRouter(prefix="/scheduling", tags=["scheduling"])


@router.post("/run", response_model=ScheduleRunResponse)
def run_schedule(request: ScheduleRunRequest) -> ScheduleRunResponse:
    dataset = get_dataset(scale=request.scale, seed=request.seed)
    return ScheduleRunResponse(**solve_schedule_problem(dataset))
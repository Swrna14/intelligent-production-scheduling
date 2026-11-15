from __future__ import annotations

from fastapi import APIRouter

from ..schemas.api import DashboardSummary
from ..services.dataset_service import get_dataset


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary() -> DashboardSummary:
    dataset = get_dataset()
    orders = dataset["production_orders"]
    urgent_orders = int((orders["priority"] == "urgent").sum()) if "priority" in orders else 0

    return DashboardSummary(
        total_products=len(dataset["products"]),
        total_machines=len(dataset["machines"]),
        total_orders=len(orders),
        total_schedules=len(dataset["operation_schedules"]),
        total_materials=len(dataset["materials"]),
        urgent_orders=urgent_orders,
    )
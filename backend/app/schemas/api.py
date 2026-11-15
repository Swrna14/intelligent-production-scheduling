from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    total_products: int
    total_machines: int
    total_orders: int
    total_schedules: int
    total_materials: int
    urgent_orders: int


class DatasetPage(BaseModel):
    dataset: str
    total: int
    limit: int
    offset: int
    items: list[dict[str, Any]]


class ScheduleRunRequest(BaseModel):
    scale: Literal["starter", "full"] = "starter"
    seed: int = Field(default=20261022, ge=0)


class ScheduleRunResponse(BaseModel):
    feasible: bool
    objective_value: float | None
    assignments: list[dict[str, Any]]
    reason: str
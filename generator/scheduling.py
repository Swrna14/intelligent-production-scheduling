from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

try:
    from ortools.sat.python import cp_model
except Exception:  # pragma: no cover - environment-specific native dependency issue
    cp_model = None


@dataclass
class JobAssignment:
    job_id: int
    machine_id: int
    start_minute: int
    end_minute: int
    status: str = "scheduled"


def build_schedule_problem(dataset: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Build a simplified scheduling model around each operation and eligible machine."""
    operations = dataset.get("operations", pd.DataFrame())
    machines = dataset.get("machines", pd.DataFrame())
    production_orders = dataset.get("production_orders", pd.DataFrame())

    if operations.empty or machines.empty or production_orders.empty:
        return {"jobs": [], "machines": [], "objective": "base"}

    jobs = []
    for _, order in production_orders.head(10).iterrows():
        order_id = int(order["order_id"])
        jobs.append(
            {
                "order_id": order_id,
                "priority": order["priority"],
                "due_date": order["due_date"],
                "job_id": order_id,
                "duration": 60,
                "machine_ids": list(machines["machine_id"].astype(int).tolist())[: min(3, len(machines))],
            }
        )

    return {"jobs": jobs, "machines": machines["machine_id"].astype(int).tolist(), "objective": "weighted_completion"}


def _fallback_schedule(dataset: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Fallback schedule generator used when the native OR-Tools binary is blocked by environment policy."""
    problems = build_schedule_problem(dataset)
    assignments: list[dict[str, Any]] = []
    for idx, job in enumerate(problems["jobs"]):
        machine_id = job["machine_ids"][idx % len(job["machine_ids"])]
        start_minute = idx * 60
        end_minute = start_minute + job["duration"]
        assignments.append(
            {
                "job_id": job["job_id"],
                "machine_id": machine_id,
                "start_minute": start_minute,
                "end_minute": end_minute,
                "status": "scheduled",
            }
        )

    return {
        "feasible": True,
        "objective_value": sum(item["end_minute"] for item in assignments),
        "assignments": assignments,
        "reason": "Fallback heuristic scheduling used because OR-Tools native dependency is blocked in this environment.",
    }


def solve_schedule_problem(dataset: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Solve a lightweight CP-SAT scheduling instance for the baseline dataset."""
    if cp_model is None:
        return _fallback_schedule(dataset)

    problem = build_schedule_problem(dataset)
    assignments: list[dict[str, Any]] = []
    model = cp_model.CpModel()

    if not problem["jobs"]:
        return {"feasible": False, "objective_value": None, "assignments": assignments, "reason": "No jobs to schedule."}

    start_vars: dict[tuple[int, int], Any] = {}
    end_vars: dict[tuple[int, int], Any] = {}
    machine_vars: dict[tuple[int, int], Any] = {}

    horizon = 24 * 60 * 5
    for job in problem["jobs"]:
        for machine_id in job["machine_ids"]:
            start = model.NewIntVar(0, horizon, f"start_{job['job_id']}_{machine_id}")
            end = model.NewIntVar(0, horizon, f"end_{job['job_id']}_{machine_id}")
            machine_choice = model.NewBoolVar(f"machine_{job['job_id']}_{machine_id}")
            start_vars[(job["job_id"], machine_id)] = start
            end_vars[(job["job_id"], machine_id)] = end
            machine_vars[(job["job_id"], machine_id)] = machine_choice
            model.Add(end == start + job["duration"])
            model.Add(start >= 0)

    for job in problem["jobs"]:
        vars_for_job = [machine_vars[(job["job_id"], machine_id)] for machine_id in job["machine_ids"]]
        model.Add(sum(vars_for_job) == 1)

    makespan = model.NewIntVar(0, horizon, "makespan")
    for job in problem["jobs"]:
        for machine_id in job["machine_ids"]:
            model.Add(end_vars[(job["job_id"], machine_id)] <= makespan)

    objective_terms: list[Any] = []
    for job in problem["jobs"]:
        for machine_id in job["machine_ids"]:
            priority_weight = 1 if job["priority"] == "normal" else 2 if job["priority"] == "urgent" else 3
            objective_terms.append(priority_weight * start_vars[(job["job_id"], machine_id)])
    objective_terms.append(10 * makespan)
    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for job in problem["jobs"]:
            for machine_id in job["machine_ids"]:
                if solver.Value(machine_vars[(job["job_id"], machine_id)]) == 1:
                    assignments.append(
                        {
                            "job_id": job["job_id"],
                            "machine_id": machine_id,
                            "start_minute": solver.Value(start_vars[(job["job_id"], machine_id)]),
                            "end_minute": solver.Value(end_vars[(job["job_id"], machine_id)]),
                            "status": "scheduled",
                        }
                    )
                    break

        return {
            "feasible": True,
            "objective_value": solver.ObjectiveValue(),
            "assignments": assignments,
            "reason": "Model solved successfully.",
        }

    return {
        "feasible": False,
        "objective_value": None,
        "assignments": assignments,
        "reason": "No feasible schedule found under the current constraints.",
    }

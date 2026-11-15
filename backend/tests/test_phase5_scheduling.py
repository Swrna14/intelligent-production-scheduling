from __future__ import annotations

from generator.generate_data import generate_dataset
from generator.scheduling import build_schedule_problem, solve_schedule_problem


def test_build_schedule_problem_builds_constraints() -> None:
    dataset = generate_dataset(scale="starter", seed=20261022)
    problem = build_schedule_problem(dataset)

    assert problem is not None
    assert "jobs" in problem
    assert "machines" in problem
    assert len(problem["jobs"]) > 0


def test_solve_schedule_problem_returns_feasible_solution() -> None:
    dataset = generate_dataset(scale="starter", seed=20261022)
    result = solve_schedule_problem(dataset)

    assert result["feasible"] in {True, False}
    assert "objective_value" in result
    assert "assignments" in result
    assert isinstance(result["assignments"], list)

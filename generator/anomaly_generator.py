from __future__ import annotations

from typing import Any

import pandas as pd


def generate_anomalies(dataset: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create isolated, labelled anomaly records for negative scenarios.

    The generated anomalies are intentionally separate from the valid baseline data
    and are tagged with metadata used for evaluation and ground-truth review.
    """
    anomalies: list[dict[str, Any]] = []

    production_orders = dataset.get("production_orders", pd.DataFrame())
    operation_schedules = dataset.get("operation_schedules", pd.DataFrame())
    material_requirements = dataset.get("material_requirements", pd.DataFrame())

    if not production_orders.empty:
        anomalies.append(
            {
                "issue_type": "machine_operation_overlap",
                "ground_truth_label": "negative_case_machine_overlap",
                "affected_entity_id": str(production_orders.iloc[0]["order_code"]),
                "expected_result": "Flag overlap between machine assignments on the same time window.",
            }
        )

    if not operation_schedules.empty:
        anomalies.append(
            {
                "issue_type": "routing_precedence_violation",
                "ground_truth_label": "negative_case_routing_precedence",
                "affected_entity_id": str(operation_schedules.iloc[0]["schedule_code"]),
                "expected_result": "Reject schedule when operation sequence violates routing precedence.",
            }
        )

    if not material_requirements.empty:
        anomalies.append(
            {
                "issue_type": "material_consumed_before_availability",
                "ground_truth_label": "negative_case_material_availability",
                "affected_entity_id": str(material_requirements.iloc[0]["requirement_id"]),
                "expected_result": "Block start when required material is not yet available.",
            }
        )

    anomalies.append(
        {
            "issue_type": "operation_scheduled_outside_shift_calendar",
            "ground_truth_label": "negative_case_shift_calendar",
            "affected_entity_id": "MACH-001",
            "expected_result": "Reject schedules outside permitted shift hours.",
        }
    )

    anomalies.append(
        {
            "issue_type": "missing_changeover_time",
            "ground_truth_label": "negative_case_changeover",
            "affected_entity_id": "MACH-002",
            "expected_result": "Require the minimum changeover duration before next job starts.",
        }
    )

    return pd.DataFrame(anomalies, columns=["issue_type", "ground_truth_label", "affected_entity_id", "expected_result"])

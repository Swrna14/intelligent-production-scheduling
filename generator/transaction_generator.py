from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

from .master_generator import build_master_data, build_operation_data, build_routing_data


def generate_transactions(scale: str = "starter", seed: int = 20261022) -> dict[str, pd.DataFrame]:
    """Generate transaction and event tables for a reproducible schedule baseline."""
    if scale not in {"starter", "full"}:
        raise ValueError(f"Unsupported scale '{scale}'. Use 'starter' or 'full'.")

    master = build_master_data(scale=scale, seed=seed)
    products = master["products"]
    machines = master["machines"]
    materials = master["materials"]
    routings = build_routing_data(products)
    operations = build_operation_data(routings)
    order_count = 51 if scale == "starter" else 501
    rng = np.random.default_rng(seed)

    start_date = datetime(2026, 1, 2)
    order_rows: list[dict[str, Any]] = []
    material_requirement_rows: list[dict[str, Any]] = []
    lot_rows: list[dict[str, Any]] = []
    schedule_rows: list[dict[str, Any]] = []
    downtime_rows: list[dict[str, Any]] = []
    tooling_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    status_history_rows: list[dict[str, Any]] = []

    for idx in range(1, order_count + 1):
        product_row = products.iloc[(idx - 1) % len(products)]
        due_offset = 10 + ((idx * 3) % 25)
        due_date = (start_date + timedelta(days=due_offset)).date()
        order_code = f"PROD-2026-{idx:06d}"
        priority = ["normal", "urgent", "high"][idx % 3]
        status = "pending" if idx % 4 else "scheduled"
        order_rows.append(
            {
                "order_id": idx,
                "order_code": order_code,
                "product_id": int(product_row["product_id"]),
                "quantity": 100 + idx * 5,
                "priority": priority,
                "due_date": due_date.isoformat(),
                "planned_start": (start_date + timedelta(days=(idx % 12))).isoformat(),
                "status": status,
            }
        )

        material_ids = [((idx + material_idx) % len(materials)) + 1 for material_idx in range(3)]
        for material_idx, material_id in enumerate(material_ids, start=1):
            material_row = materials.iloc[material_id - 1]
            qty = round(10 + material_idx * 5 + (idx % 7), 2)
            material_requirement_rows.append(
                {
                    "requirement_id": len(material_requirement_rows) + 1,
                    "order_id": idx,
                    "material_id": int(material_id),
                    "quantity_required": qty,
                    "unit_of_measure": material_row["unit_of_measure"],
                    "required_by_date": (start_date + timedelta(days=idx % 10)).isoformat(),
                }
            )

        if idx <= len(materials):
            lot_id = idx
            lot_rows.append(
                {
                    "lot_id": lot_id,
                    "lot_code": f"LOT-{idx:06d}",
                    "material_id": int(material_ids[0]),
                    "quantity_on_hand": 150.0 + idx,
                    "unit_cost": round(5.0 + idx * 0.5, 2),
                    "received_at": (start_date - timedelta(days=2)).isoformat(),
                    "expiry_date": (start_date + timedelta(days=60)).date().isoformat(),
                    "supplier": f"Supplier {idx % 10 + 1}",
                }
            )

        order_operation_count = 4
        for op_idx in range(1, order_operation_count + 1):
            operation_row = operations.iloc[((idx + op_idx) % len(operations))]
            machine_row = machines.iloc[(idx + op_idx) % len(machines)]
            start_dt = start_date + timedelta(days=(idx % 12) + op_idx, hours=8 + ((idx + op_idx) % 8))
            end_dt = start_dt + timedelta(minutes=int(operation_row["default_duration_min"]))
            schedule_rows.append(
                {
                    "schedule_id": len(schedule_rows) + 1,
                    "schedule_code": f"SCH-{idx:06d}-{op_idx:02d}",
                    "order_id": idx,
                    "operation_id": int(operation_row["operation_id"]),
                    "machine_id": int(machine_row["machine_id"]),
                    "planned_start": start_dt.isoformat(),
                    "planned_end": end_dt.isoformat(),
                    "actual_start": start_dt.isoformat(),
                    "actual_end": end_dt.isoformat(),
                    "status": "scheduled",
                    "scheduled_by": "system",
                }
            )

        event_rows.append(
            {
                "event_id": len(event_rows) + 1,
                "order_id": idx,
                "schedule_id": len(schedule_rows),
                "event_type": "status_changed",
                "event_time": (start_date + timedelta(days=idx % 7)).isoformat(),
                "details": f"Order {idx} entered scheduled state.",
            }
        )

        status_history_rows.append(
            {
                "history_id": len(status_history_rows) + 1,
                "order_id": idx,
                "previous_status": "pending",
                "new_status": status,
                "changed_at": (start_date + timedelta(days=idx % 5)).isoformat(),
                "reason": "Initial baseline scheduling",
                "actor": "system",
            }
        )

    for machine_idx in range(1, len(machines) + 1):
        if machine_idx % 4 == 0:
            downtime_rows.append(
                {
                    "downtime_id": len(downtime_rows) + 1,
                    "machine_id": machine_idx,
                    "downtime_start": (start_date + timedelta(days=machine_idx % 12, hours=9)).isoformat(),
                    "downtime_end": (start_date + timedelta(days=machine_idx % 12, hours=12)).isoformat(),
                    "reason": "Preventive maintenance",
                    "maintenance_type": "planned",
                }
            )

    for tool_idx in range(1, 7):
        tooling_rows.append(
            {
                "tooling_id": tool_idx,
                "tooling_code": f"TOOL-{tool_idx:03d}",
                "tool_name": f"Tool {tool_idx}",
                "available_capacity": 1 + (tool_idx % 2),
                "location": f"Area-{tool_idx % 5 + 1}",
                "effective_from": "2026-01-01",
            }
        )

    production_orders = pd.DataFrame(order_rows)
    material_requirements = pd.DataFrame(material_requirement_rows)
    inventory_lots_df = pd.DataFrame(lot_rows)
    operation_schedules = pd.DataFrame(schedule_rows)
    machine_downtime_df = pd.DataFrame(downtime_rows)
    shared_tooling = pd.DataFrame(tooling_rows)
    order_status_history = pd.DataFrame(status_history_rows)
    schedule_events = pd.DataFrame(event_rows)

    return {
        "production_orders": production_orders,
        "material_requirements": material_requirements,
        "inventory_lots": inventory_lots_df,
        "operation_schedules": operation_schedules,
        "machine_downtime": machine_downtime_df,
        "shared_tooling": shared_tooling,
        "order_status_history": order_status_history,
        "schedule_events": schedule_events,
    }

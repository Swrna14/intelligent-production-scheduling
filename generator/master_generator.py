"""Master-data generation helpers for the production scheduling system."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def build_master_data(scale: str, seed: int) -> dict[str, pd.DataFrame]:
    """Build the core master tables used by the scheduling engine."""
    config = {
        "starter": {"products": 20, "machines": 8, "materials": 40, "orders": 50},
        "full": {"products": 100, "machines": 40, "materials": 200, "orders": 500},
    }
    settings = config[scale]
    rng = np.random.default_rng(seed)

    product_families = ["Mechanical", "Electrical", "Assembly", "Packaging", "Coating", "Machining"]
    families = [product_families[i % len(product_families)] for i in range(settings["products"])]

    products = pd.DataFrame(
        {
            "product_id": list(range(1, settings["products"] + 1)),
            "product_code": [f"PROD-2026-{idx:06d}" for idx in range(1, settings["products"] + 1)],
            "sku": [f"SKU-{idx:06d}" for idx in range(1, settings["products"] + 1)],
            "product_name": [f"{family} Item {idx:03d}" for idx, family in enumerate(families, start=1)],
            "product_family": families,
            "standard_cost": (rng.uniform(10.0, 100.0, settings["products"]) * 10).round(2),
            "lead_time_days": rng.integers(3, 12, size=settings["products"]) + 1,
            "active": [True] * settings["products"],
        }
    )

    machines = pd.DataFrame(
        {
            "machine_id": list(range(1, settings["machines"] + 1)),
            "machine_code": [f"MACH-{idx:03d}" for idx in range(1, settings["machines"] + 1)],
            "machine_name": [f"Machine {idx:03d}" for idx in range(1, settings["machines"] + 1)],
            "machine_type": ["CNC" if idx % 2 else "Assembly" for idx in range(1, settings["machines"] + 1)],
            "capacity_per_shift": rng.integers(1, 4, size=settings["machines"]).tolist(),
            "status": ["available"] * settings["machines"],
            "location": [f"Cell-{(idx % 5) + 1}" for idx in range(1, settings["machines"] + 1)],
            "base_rate": (rng.uniform(35.0, 120.0, settings["machines"]) * 10).round(2),
        }
    )

    materials = pd.DataFrame(
        {
            "material_id": list(range(1, settings["materials"] + 1)),
            "material_code": [f"MAT-{idx:06d}" for idx in range(1, settings["materials"] + 1)],
            "material_name": [f"Material {idx:06d}" for idx in range(1, settings["materials"] + 1)],
            "unit_of_measure": ["kg" if idx % 2 else "pcs" for idx in range(1, settings["materials"] + 1)],
            "reorder_point": (rng.uniform(5.0, 150.0, settings["materials"]) * 10).round(2),
            "lead_time_days": rng.integers(1, 10, size=settings["materials"]).tolist(),
        }
    )

    return {"products": products, "machines": machines, "materials": materials}


def build_routing_data(products: pd.DataFrame) -> pd.DataFrame:
    routings: list[dict[str, Any]] = []
    for row in products.itertuples(index=False):
        for version in [1]:
            routings.append(
                {
                    "routing_id": len(routings) + 1,
                    "routing_code": f"ROUTE-{row.sku}-01",
                    "product_id": row.product_id,
                    "product_code": row.product_code,
                    "version": version,
                    "effective_from": "2026-01-01",
                }
            )
    return pd.DataFrame(routings)


def build_operation_data(routings: pd.DataFrame) -> pd.DataFrame:
    operations: list[dict[str, Any]] = []
    for row in routings.itertuples(index=False):
        for seq in (1, 2, 3, 4):
            operations.append(
                {
                    "operation_id": len(operations) + 1,
                    "operation_code": f"OP-{row.product_code}-{seq:02d}",
                    "routing_id": row.routing_id,
                    "sequence_no": seq,
                    "operation_name": f"Step {seq}",
                    "default_duration_min": 60 + (seq * 25),
                    "setup_time_min": 15 + seq * 5,
                    "tooling_group": f"TG-{seq}",
                }
            )
    return pd.DataFrame(operations)

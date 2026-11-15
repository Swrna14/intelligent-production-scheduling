from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from generator.generate_data import generate_dataset


DATA_DIR = Path(__file__).resolve().parents[3] / "data"
DEFAULT_EXPORT = DATA_DIR / "exports" / "generated_dataset.json"
DATASET_NAMES = {
    "products",
    "machines",
    "materials",
    "routings",
    "operations",
    "production_orders",
    "material_requirements",
    "inventory_lots",
    "operation_schedules",
    "machine_downtime",
    "shared_tooling",
    "order_status_history",
    "schedule_events",
    "anomalies",
}


def get_dataset(scale: str = "starter", seed: int = 20261022) -> dict[str, pd.DataFrame]:
    """Load the checked-in starter export, generating data for other inputs."""
    if scale == "starter" and seed == 20261022 and DEFAULT_EXPORT.is_file():
        with DEFAULT_EXPORT.open(encoding="utf-8") as handle:
            exported = json.load(handle)
        return {name: pd.DataFrame(exported.get(name, [])) for name in DATASET_NAMES}

    return generate_dataset(scale=scale, seed=seed)
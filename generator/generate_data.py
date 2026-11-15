from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .anomaly_generator import generate_anomalies
from .master_generator import build_master_data, build_operation_data, build_routing_data
from .transaction_generator import generate_transactions


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)


def generate_dataset(scale: str = "starter", seed: int = 20261022) -> dict[str, pd.DataFrame]:
    """Generate master and transaction data for the selected scale.

    The output is deterministic for the same scale and seed, which allows easy
    reproducibility checks across repeated runs.
    """
    if scale not in {"starter", "full"}:
        raise ValueError(f"Unsupported scale '{scale}'. Use 'starter' or 'full'.")

    master = build_master_data(scale=scale, seed=seed)
    products = master["products"]
    machines = master["machines"]
    materials = master["materials"]
    routings = build_routing_data(products)
    operations = build_operation_data(routings)

    transactions = generate_transactions(scale=scale, seed=seed)
    anomalies = generate_anomalies(transactions)

    datasets = {
        "products": products,
        "machines": machines,
        "materials": materials,
        "routings": routings,
        "operations": operations,
        "production_orders": transactions["production_orders"],
        "material_requirements": transactions["material_requirements"],
        "inventory_lots": transactions["inventory_lots"],
        "operation_schedules": transactions["operation_schedules"],
        "machine_downtime": transactions["machine_downtime"],
        "shared_tooling": transactions["shared_tooling"],
        "order_status_history": transactions["order_status_history"],
        "schedule_events": transactions["schedule_events"],
        "anomalies": anomalies,
    }

    master_dir = DATA_DIR / "master"
    transactions_dir = DATA_DIR / "transactions"
    events_dir = DATA_DIR / "events"
    ground_truth_dir = DATA_DIR / "ground_truth"

    for name, df in datasets.items():
        if name in {"products", "machines", "materials", "routings", "operations"}:
            _write_csv(df, master_dir / f"{name}.csv")
        elif name == "anomalies":
            _write_csv(df, ground_truth_dir / "ground_truth.csv")
        else:
            _write_csv(df, transactions_dir / f"{name}.csv")

    _write_json({name: df.to_dict(orient="records") for name, df in datasets.items()}, DATA_DIR / "exports" / "generated_dataset.json")
    _write_json({"anomalies": anomalies.to_dict(orient="records")}, ground_truth_dir / "ground_truth.json")

    return datasets


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate reproducible manufacturing master data.")
    parser.add_argument("--scale", choices=["starter", "full"], default="starter", help="Dataset size preset.")
    parser.add_argument("--seed", type=int, default=20261022, help="Random seed used for deterministic generation.")
    args = parser.parse_args()
    generate_dataset(scale=args.scale, seed=args.seed)
    print(f"Generated dataset for scale={args.scale} with seed={args.seed}")


if __name__ == "__main__":
    main()

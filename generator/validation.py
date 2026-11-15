from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .anomaly_generator import generate_anomalies

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"


def _iter_table_records(dataset: dict[str, pd.DataFrame]) -> Iterable[tuple[str, pd.DataFrame]]:
    for table_name, frame in dataset.items():
        if isinstance(frame, pd.DataFrame):
            yield table_name, frame


def _count_missing_values(frame: pd.DataFrame) -> int:
    return int(frame.isna().sum().sum())


def _validate_primary_keys(dataset: dict[str, pd.DataFrame]) -> tuple[list[str], list[str]]:
    error_messages: list[str] = []
    valid_messages: list[str] = []
    id_fields = {
        "products": ["product_id", "product_code"],
        "machines": ["machine_id", "machine_code"],
        "materials": ["material_id", "material_code"],
        "routings": ["routing_id", "routing_code"],
        "operations": ["operation_id", "operation_code"],
        "production_orders": ["order_id", "order_code"],
        "inventory_lots": ["lot_id", "lot_code"],
        "operation_schedules": ["schedule_id", "schedule_code"],
        "shared_tooling": ["tooling_id", "tooling_code"],
    }

    for table_name, frame in _iter_table_records(dataset):
        if frame.empty:
            continue
        for candidate in id_fields.get(table_name, []):
            if candidate in frame.columns:
                duplicates = frame[frame[candidate].duplicated(keep=False)]
                if not duplicates.empty:
                    error_messages.append(f"{table_name}.{candidate} has duplicate values")
                else:
                    valid_messages.append(f"{table_name}.{candidate} unique")
    return valid_messages, error_messages


def _validate_foreign_keys(dataset: dict[str, pd.DataFrame]) -> tuple[list[str], list[str]]:
    valid_messages: list[str] = []
    error_messages: list[str] = []

    relationship_checks = {
        "production_orders": [("product_id", "products", "product_id")],
        "operation_schedules": [("order_id", "production_orders", "order_id"), ("machine_id", "machines", "machine_id")],
        "inventory_lots": [("material_id", "materials", "material_id")],
        "material_requirements": [("material_id", "materials", "material_id")],
        "operation_schedules": [("order_id", "production_orders", "order_id"), ("machine_id", "machines", "machine_id")],
    }

    for child_table, checks in relationship_checks.items():
        if child_table not in dataset:
            continue
        child_frame = dataset[child_table]
        if child_frame.empty:
            continue
        for child_col, parent_table, parent_col in checks:
            if parent_table not in dataset or child_col not in child_frame.columns or parent_col not in dataset[parent_table].columns:
                continue
            parent_values = set(dataset[parent_table][parent_col].dropna().astype(str).tolist())
            invalid_values = child_frame[~child_frame[child_col].astype(str).isin(parent_values)][child_col].dropna().tolist()
            if invalid_values:
                error_messages.append(f"{child_table}.{child_col} references missing {parent_table}.{parent_col}: {invalid_values[:3]}")
            else:
                valid_messages.append(f"{child_table}.{child_col} references valid {parent_table}.{parent_col}")
    return valid_messages, error_messages


def _validate_date_columns(dataset: dict[str, pd.DataFrame]) -> tuple[list[str], list[str]]:
    valid_messages: list[str] = []
    error_messages: list[str] = []
    date_columns = [
        "due_date",
        "planned_start",
        "planned_end",
        "received_at",
        "required_by_date",
        "downtime_start",
        "downtime_end",
        "effective_from",
        "effective_to",
        "created_at",
        "updated_at",
    ]
    for table_name, frame in _iter_table_records(dataset):
        for column in date_columns:
            if column not in frame.columns:
                continue
            parsed = pd.to_datetime(frame[column], errors="coerce")
            invalid = frame[parsed.isna() & frame[column].notna()]
            if invalid.empty:
                valid_messages.append(f"{table_name}.{column} date format valid")
            else:
                error_messages.append(f"{table_name}.{column} contains invalid date values")
    return valid_messages, error_messages


def _validate_sequence_and_capacity(dataset: dict[str, pd.DataFrame]) -> tuple[list[str], list[str]]:
    valid_messages: list[str] = []
    error_messages: list[str] = []
    if "operation_schedules" in dataset and not dataset["operation_schedules"].empty:
        schedule_df = dataset["operation_schedules"]
        duplicates = schedule_df["schedule_code"].duplicated(keep=False)
        if duplicates.any():
            error_messages.append("operation_schedules.schedule_code contains duplicates")
        else:
            valid_messages.append("operation_schedules.schedule_code unique")

        if {"order_id", "operation_id", "planned_start", "planned_end"}.issubset(schedule_df.columns):
            grouped = schedule_df.groupby("order_id")
            for _, group in grouped:
                ordered = group.sort_values("planned_start")
                if ordered["operation_id"].duplicated().any():
                    error_messages.append(f"order {group['order_id'].iloc[0]} has duplicate operation schedule entries")
                else:
                    valid_messages.append(f"order {group['order_id'].iloc[0]} sequence valid")

    if "production_orders" in dataset and "quantity" in dataset["production_orders"].columns:
        quantity_invalid = dataset["production_orders"][dataset["production_orders"]["quantity"] <= 0]
        if quantity_invalid.empty:
            valid_messages.append("production_orders.quantity valid")
        else:
            error_messages.append("production_orders.quantity includes non-positive values")

    return valid_messages, error_messages


def build_validation_report(dataset: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Generate a validation summary for the baseline dataset and anomaly-free schedule data."""
    total_records = 0
    valid_records = 0
    invalid_records = 0
    errors_by_category: dict[str, list[str]] = {}
    exceptions: list[str] = []
    all_valid_messages: list[str] = []
    all_error_messages: list[str] = []

    for _, frame in _iter_table_records(dataset):
        total_records += int(len(frame))

    try:
        pk_valid, pk_errors = _validate_primary_keys(dataset)
        all_valid_messages.extend(pk_valid)
        all_error_messages.extend(pk_errors)
    except Exception as exc:  # pragma: no cover - defensive validation path
        exceptions.append(f"primary_key_validation_error: {exc}")

    try:
        fk_valid, fk_errors = _validate_foreign_keys(dataset)
        all_valid_messages.extend(fk_valid)
        all_error_messages.extend(fk_errors)
    except Exception as exc:  # pragma: no cover - defensive validation path
        exceptions.append(f"foreign_key_validation_error: {exc}")

    try:
        date_valid, date_errors = _validate_date_columns(dataset)
        all_valid_messages.extend(date_valid)
        all_error_messages.extend(date_errors)
    except Exception as exc:  # pragma: no cover - defensive validation path
        exceptions.append(f"date_validation_error: {exc}")

    try:
        seq_valid, seq_errors = _validate_sequence_and_capacity(dataset)
        all_valid_messages.extend(seq_valid)
        all_error_messages.extend(seq_errors)
    except Exception as exc:  # pragma: no cover - defensive validation path
        exceptions.append(f"sequence_capacity_validation_error: {exc}")

    for table_name, frame in _iter_table_records(dataset):
        missing_count = _count_missing_values(frame)
        if missing_count == 0:
            all_valid_messages.append(f"{table_name} missing values check passed")
        else:
            all_error_messages.append(f"{table_name} has {missing_count} missing values")

    if all_error_messages:
        errors_by_category["validation_errors"] = all_error_messages
    if all_valid_messages:
        errors_by_category["validation_validations"] = all_valid_messages

    invalid_records = len(all_error_messages)
    valid_records = max(0, total_records - invalid_records)
    pass_status = invalid_records == 0 and not exceptions

    return {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "errors_by_category": errors_by_category,
        "exceptions": exceptions,
        "pass_status": pass_status,
    }


def export_ground_truth(dataset: dict[str, pd.DataFrame], anomalies: pd.DataFrame | None = None) -> dict[str, Any]:
    """Write the separate labelled anomaly dataset required for evaluation purposes."""
    if anomalies is None:
        anomalies = generate_anomalies(dataset)

    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
    anomalies_path = GROUND_TRUTH_DIR / "ground_truth.csv"
    anomalies_json_path = GROUND_TRUTH_DIR / "ground_truth.json"

    anomalies.to_csv(anomalies_path, index=False)
    with anomalies_json_path.open("w", encoding="utf-8") as handle:
        json.dump(anomalies.to_dict(orient="records"), handle, indent=2, default=str)

    return {"anomalies": anomalies.to_dict(orient="records")}


def validate_dataset(dataset: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Backward-compatible alias for the validation summary builder."""
    return build_validation_report(dataset)

from __future__ import annotations

from generator.anomaly_generator import generate_anomalies
from generator.generate_data import generate_dataset
from generator.transaction_generator import generate_transactions


def test_generate_transactions_returns_expected_tables() -> None:
    transactions = generate_transactions(scale="starter", seed=20261022)

    assert "production_orders" in transactions
    assert "material_requirements" in transactions
    assert "operation_schedules" in transactions
    assert "inventory_lots" in transactions
    assert "machine_downtime" in transactions
    assert "shared_tooling" in transactions
    assert len(transactions["production_orders"]) > 0
    assert len(transactions["operation_schedules"]) > 0


def test_generate_anomalies_are_isolated_and_labelled() -> None:
    dataset = generate_dataset(scale="starter", seed=20261022)
    anomalies = generate_anomalies(dataset)

    required = {"issue_type", "ground_truth_label", "affected_entity_id", "expected_result"}
    assert required.issubset(set(anomalies.columns))
    assert len(anomalies) >= 5
    assert anomalies["ground_truth_label"].nunique() >= 1
    assert anomalies["affected_entity_id"].notna().all()

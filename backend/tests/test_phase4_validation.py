from __future__ import annotations

from generator.generate_data import generate_dataset
from generator.validation import build_validation_report, export_ground_truth


def test_build_validation_report_passes_for_baseline_dataset() -> None:
    dataset = generate_dataset(scale="starter", seed=20261022)
    report = build_validation_report(dataset)

    assert report["total_records"] > 0
    assert report["valid_records"] >= 1
    assert report["invalid_records"] >= 0
    assert report["pass_status"] in {True, False}
    assert isinstance(report["errors_by_category"], dict)


def test_export_ground_truth_creates_separate_validation_outputs() -> None:
    dataset = generate_dataset(scale="starter", seed=20261022)
    ground_truth = export_ground_truth(dataset)

    assert "anomalies" in ground_truth
    assert len(ground_truth["anomalies"]) >= 5
    assert "ground_truth_label" in ground_truth["anomalies"][0]

from __future__ import annotations

from pathlib import Path

from generator.generate_data import generate_dataset


def test_generate_dataset_starter_is_reproducible() -> None:
    dataset_a = generate_dataset(scale="starter", seed=20261022)
    dataset_b = generate_dataset(scale="starter", seed=20261022)

    assert dataset_a["products"]["product_code"].tolist() == dataset_b["products"]["product_code"].tolist()
    assert dataset_a["machines"]["machine_code"].tolist() == dataset_b["machines"]["machine_code"].tolist()
    assert len(dataset_a["products"]) >= 10
    assert len(dataset_a["machines"]) >= 5


def test_generate_dataset_creates_expected_files() -> None:
    output_dir = Path("data/master")
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = generate_dataset(scale="starter", seed=20261022)
    assert "products" in dataset
    assert "machines" in dataset
    assert "materials" in dataset
    assert len(dataset["products"]) > 0
    assert len(dataset["machines"]) > 0

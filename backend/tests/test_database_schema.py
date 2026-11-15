from __future__ import annotations

from sqlalchemy import inspect

from backend.app.database import engine


def test_expected_tables_exist() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    expected_tables = {
        "products",
        "routings",
        "operations",
        "machines",
        "machine_calendars",
        "materials",
        "inventory_lots",
        "production_orders",
        "operation_schedules",
        "changeover_matrices",
        "routing_machine_eligibility",
        "operation_material_requirements",
        "inventory_consumption",
        "shared_tooling",
        "machine_downtime",
        "schedule_events",
        "order_status_history",
        "constraint_violations",
    }

    assert expected_tables.issubset(table_names)


def test_core_columns_present() -> None:
    inspector = inspect(engine)
    products_columns = {column["name"] for column in inspector.get_columns("products")}
    assert {"id", "product_code", "sku", "product_name", "created_at"}.issubset(products_columns)

    machine_columns = {column["name"] for column in inspector.get_columns("machines")}
    assert {"id", "machine_code", "machine_name", "status"}.issubset(machine_columns)

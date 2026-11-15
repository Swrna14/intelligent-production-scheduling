from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_code = Column(String(50), unique=True, nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(150), nullable=False)
    product_family = Column(String(50), nullable=True)
    standard_cost = Column(Float, nullable=False, default=0.0)
    lead_time_days = Column(Integer, nullable=False, default=0)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    routings = relationship("Routing", back_populates="product")
    orders = relationship("ProductionOrder", back_populates="product")


class Routing(Base):
    __tablename__ = "routings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    routing_code = Column(String(80), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="routings")
    operations = relationship("Operation", back_populates="routing")
    machine_eligibility = relationship("RoutingMachineEligibility", back_populates="routing")


class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_code = Column(String(80), unique=True, nullable=False)
    routing_id = Column(Integer, ForeignKey("routings.id"), nullable=False)
    sequence_no = Column(Integer, nullable=False)
    operation_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    default_duration_min = Column(Integer, nullable=False, default=60)
    setup_time_min = Column(Integer, nullable=False, default=15)
    tooling_group = Column(String(80), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    routing = relationship("Routing", back_populates="operations")
    material_requirements = relationship("OperationMaterialRequirement", back_populates="operation")
    schedules = relationship("OperationSchedule", back_populates="operation")


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_code = Column(String(30), unique=True, nullable=False)
    machine_name = Column(String(120), nullable=False)
    machine_type = Column(String(50), nullable=False)
    capacity_per_shift = Column(Integer, nullable=False, default=1)
    status = Column(String(30), nullable=False, default="available")
    location = Column(String(80), nullable=True)
    base_rate = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    calendars = relationship("MachineCalendar", back_populates="machine")
    eligibilities = relationship("RoutingMachineEligibility", back_populates="machine")
    downtimes = relationship("MachineDowntime", back_populates="machine")
    schedules = relationship("OperationSchedule", back_populates="machine")


class MachineCalendar(Base):
    __tablename__ = "machine_calendars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    calendar_date = Column(Date, nullable=False)
    shift_name = Column(String(30), nullable=False)
    start_time = Column(String(20), nullable=False)
    end_time = Column(String(20), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    machine = relationship("Machine", back_populates="calendars")


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_code = Column(String(50), unique=True, nullable=False)
    material_name = Column(String(150), nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    reorder_point = Column(Float, nullable=False, default=0.0)
    lead_time_days = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    lots = relationship("InventoryLot", back_populates="material")
    material_requirements = relationship("OperationMaterialRequirement", back_populates="material")
    inventory_consumption = relationship("InventoryConsumption", back_populates="material")


class InventoryLot(Base):
    __tablename__ = "inventory_lots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_code = Column(String(60), unique=True, nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity_on_hand = Column(Float, nullable=False, default=0.0)
    unit_cost = Column(Float, nullable=False, default=0.0)
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expiry_date = Column(Date, nullable=True)
    supplier = Column(String(120), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    material = relationship("Material", back_populates="lots")
    consumptions = relationship("InventoryConsumption", back_populates="lot")


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_code = Column(String(50), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    priority = Column(String(20), nullable=False, default="normal")
    due_date = Column(Date, nullable=False)
    planned_start = Column(DateTime, nullable=True)
    status = Column(String(30), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="orders")
    schedules = relationship("OperationSchedule", back_populates="order")
    status_history = relationship("OrderStatusHistory", back_populates="order")
    events = relationship("ScheduleEvent", back_populates="order")
    inventory_consumption = relationship("InventoryConsumption", back_populates="order")


class OperationSchedule(Base):
    __tablename__ = "operation_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_code = Column(String(60), unique=True, nullable=False)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    planned_start = Column(DateTime, nullable=False)
    planned_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    status = Column(String(30), nullable=False, default="scheduled")
    scheduled_by = Column(String(80), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("ProductionOrder", back_populates="schedules")
    operation = relationship("Operation", back_populates="schedules")
    machine = relationship("Machine", back_populates="schedules")
    schedule_events = relationship("ScheduleEvent", back_populates="schedule")


class ChangeoverMatrix(Base):
    __tablename__ = "changeover_matrices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    to_machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    from_product_family = Column(String(50), nullable=True)
    to_product_family = Column(String(50), nullable=True)
    minutes = Column(Integer, nullable=False, default=0)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("from_machine_id", "to_machine_id", "effective_from", name="uq_changeover_matrix"),)


class RoutingMachineEligibility(Base):
    __tablename__ = "routing_machine_eligibility"

    id = Column(Integer, primary_key=True, autoincrement=True)
    routing_id = Column(Integer, ForeignKey("routings.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    routing = relationship("Routing", back_populates="machine_eligibility")
    machine = relationship("Machine", back_populates="eligibilities")


class OperationMaterialRequirement(Base):
    __tablename__ = "operation_material_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity_required = Column(Float, nullable=False, default=0.0)
    unit_of_measure = Column(String(20), nullable=False)
    required_by_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    operation = relationship("Operation", back_populates="material_requirements")
    material = relationship("Material", back_populates="material_requirements")


class InventoryConsumption(Base):
    __tablename__ = "inventory_consumption"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("inventory_lots.id"), nullable=False)
    quantity_consumed = Column(Float, nullable=False, default=0.0)
    consumed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    order = relationship("ProductionOrder", back_populates="inventory_consumption")
    material = relationship("Material", back_populates="inventory_consumption")
    lot = relationship("InventoryLot", back_populates="consumptions")


class SharedTooling(Base):
    __tablename__ = "shared_tooling"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tooling_code = Column(String(60), unique=True, nullable=False)
    tool_name = Column(String(120), nullable=False)
    available_capacity = Column(Integer, nullable=False, default=1)
    location = Column(String(80), nullable=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class MachineDowntime(Base):
    __tablename__ = "machine_downtime"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    downtime_start = Column(DateTime, nullable=False)
    downtime_end = Column(DateTime, nullable=False)
    reason = Column(String(120), nullable=False)
    maintenance_type = Column(String(50), nullable=False, default="planned")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    machine = relationship("Machine", back_populates="downtimes")


class ScheduleEvent(Base):
    __tablename__ = "schedule_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("operation_schedules.id"), nullable=False)
    previous_machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    new_machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    previous_start = Column(DateTime, nullable=True)
    new_start = Column(DateTime, nullable=True)
    change_reason = Column(Text, nullable=False)
    actor = Column(String(80), nullable=False, default="system")
    event_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    order = relationship("ProductionOrder", back_populates="events")
    schedule = relationship("OperationSchedule", back_populates="schedule_events")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    previous_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reason = Column(Text, nullable=True)
    actor = Column(String(80), nullable=False, default="system")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    order = relationship("ProductionOrder", back_populates="status_history")


class ConstraintViolation(Base):
    __tablename__ = "constraint_violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(String(80), nullable=False)
    violation_type = Column(String(80), nullable=False)
    issue_detail = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default="medium")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("entity_type", "entity_id", "violation_type", name="uq_constraint_violation"),)

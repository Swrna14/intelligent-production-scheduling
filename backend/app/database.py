from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./production_scheduling.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def init_db() -> None:
    """Create all database tables defined in the SQLAlchemy metadata."""
    from .models.entities import (  # noqa: F401
        ChangeoverMatrix,
        ConstraintViolation,
        InventoryConsumption,
        InventoryLot,
        Machine,
        MachineCalendar,
        MachineDowntime,
        Material,
        Operation,
        OperationMaterialRequirement,
        OperationSchedule,
        OrderStatusHistory,
        ProductionOrder,
        Product,
        Routing,
        RoutingMachineEligibility,
        ScheduleEvent,
        SharedTooling,
    )

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


init_db()

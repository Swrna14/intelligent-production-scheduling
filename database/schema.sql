CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    sku VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(150) NOT NULL,
    product_family VARCHAR(50),
    standard_cost REAL NOT NULL DEFAULT 0.0,
    lead_time_days INTEGER NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    routing_code VARCHAR(80) NOT NULL UNIQUE,
    product_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    description TEXT,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_code VARCHAR(80) NOT NULL UNIQUE,
    routing_id INTEGER NOT NULL,
    sequence_no INTEGER NOT NULL,
    operation_name VARCHAR(100) NOT NULL,
    description TEXT,
    default_duration_min INTEGER NOT NULL DEFAULT 60,
    setup_time_min INTEGER NOT NULL DEFAULT 15,
    tooling_group VARCHAR(80),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (routing_id) REFERENCES routings(id)
);

CREATE TABLE IF NOT EXISTS machines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_code VARCHAR(30) NOT NULL UNIQUE,
    machine_name VARCHAR(120) NOT NULL,
    machine_type VARCHAR(50) NOT NULL,
    capacity_per_shift INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(30) NOT NULL DEFAULT 'available',
    location VARCHAR(80),
    base_rate REAL NOT NULL DEFAULT 0.0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS machine_calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id INTEGER NOT NULL,
    calendar_date DATE NOT NULL,
    shift_name VARCHAR(30) NOT NULL,
    start_time VARCHAR(20) NOT NULL,
    end_time VARCHAR(20) NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_code VARCHAR(50) NOT NULL UNIQUE,
    material_name VARCHAR(150) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL,
    reorder_point REAL NOT NULL DEFAULT 0.0,
    lead_time_days INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_code VARCHAR(60) NOT NULL UNIQUE,
    material_id INTEGER NOT NULL,
    quantity_on_hand REAL NOT NULL DEFAULT 0.0,
    unit_cost REAL NOT NULL DEFAULT 0.0,
    received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATE,
    supplier VARCHAR(120),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

CREATE TABLE IF NOT EXISTS production_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_code VARCHAR(50) NOT NULL UNIQUE,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
    due_date DATE NOT NULL,
    planned_start DATETIME,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS operation_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_code VARCHAR(60) NOT NULL UNIQUE,
    order_id INTEGER NOT NULL,
    operation_id INTEGER NOT NULL,
    machine_id INTEGER NOT NULL,
    planned_start DATETIME NOT NULL,
    planned_end DATETIME NOT NULL,
    actual_start DATETIME,
    actual_end DATETIME,
    status VARCHAR(30) NOT NULL DEFAULT 'scheduled',
    scheduled_by VARCHAR(80),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES production_orders(id),
    FOREIGN KEY (operation_id) REFERENCES operations(id),
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

CREATE TABLE IF NOT EXISTS changeover_matrices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_machine_id INTEGER NOT NULL,
    to_machine_id INTEGER NOT NULL,
    from_product_family VARCHAR(50),
    to_product_family VARCHAR(50),
    minutes INTEGER NOT NULL DEFAULT 0,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (from_machine_id, to_machine_id, effective_from),
    FOREIGN KEY (from_machine_id) REFERENCES machines(id),
    FOREIGN KEY (to_machine_id) REFERENCES machines(id)
);

CREATE TABLE IF NOT EXISTS routing_machine_eligibility (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    routing_id INTEGER NOT NULL,
    machine_id INTEGER NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (routing_id) REFERENCES routings(id),
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

CREATE TABLE IF NOT EXISTS operation_material_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    quantity_required REAL NOT NULL DEFAULT 0.0,
    unit_of_measure VARCHAR(20) NOT NULL,
    required_by_date DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES operations(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

CREATE TABLE IF NOT EXISTS inventory_consumption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    operation_id INTEGER,
    material_id INTEGER NOT NULL,
    lot_id INTEGER NOT NULL,
    quantity_consumed REAL NOT NULL DEFAULT 0.0,
    consumed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES production_orders(id),
    FOREIGN KEY (operation_id) REFERENCES operations(id),
    FOREIGN KEY (material_id) REFERENCES materials(id),
    FOREIGN KEY (lot_id) REFERENCES inventory_lots(id)
);

CREATE TABLE IF NOT EXISTS shared_tooling (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tooling_code VARCHAR(60) NOT NULL UNIQUE,
    tool_name VARCHAR(120) NOT NULL,
    available_capacity INTEGER NOT NULL DEFAULT 1,
    location VARCHAR(80),
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS machine_downtime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id INTEGER NOT NULL,
    downtime_start DATETIME NOT NULL,
    downtime_end DATETIME NOT NULL,
    reason VARCHAR(120) NOT NULL,
    maintenance_type VARCHAR(50) NOT NULL DEFAULT 'planned',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

CREATE TABLE IF NOT EXISTS schedule_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    schedule_id INTEGER NOT NULL,
    previous_machine_id INTEGER,
    new_machine_id INTEGER,
    previous_start DATETIME,
    new_start DATETIME,
    change_reason TEXT NOT NULL,
    actor VARCHAR(80) NOT NULL DEFAULT 'system',
    event_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES production_orders(id),
    FOREIGN KEY (schedule_id) REFERENCES operation_schedules(id),
    FOREIGN KEY (previous_machine_id) REFERENCES machines(id),
    FOREIGN KEY (new_machine_id) REFERENCES machines(id)
);

CREATE TABLE IF NOT EXISTS order_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    previous_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    actor VARCHAR(80) NOT NULL DEFAULT 'system',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES production_orders(id)
);

CREATE TABLE IF NOT EXISTS constraint_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(80) NOT NULL,
    entity_id VARCHAR(80) NOT NULL,
    violation_type VARCHAR(80) NOT NULL,
    issue_detail TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (entity_type, entity_id, violation_type)
);

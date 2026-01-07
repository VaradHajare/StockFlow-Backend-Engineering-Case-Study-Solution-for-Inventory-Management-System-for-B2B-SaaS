-- Part 2: Database Design

-- 1. COMPANIES
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. WAREHOUSES
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_warehouse_company ON warehouses (company_id);

-- 3. SUPPLIERS
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50)
);

-- 4. PRODUCTS
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    description TEXT,
    is_bundle BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_product_sku ON products(sku);
CREATE INDEX idx_product_company ON products (company_id);

-- 5. PRODUCT_BUNDLES
CREATE TABLE product_bundles (
    parent_product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    child_product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE RESTRICT,
    quantity_required INTEGER NOT NULL CHECK (quantity_required > 0),
    PRIMARY KEY (parent_product_id, child_product_id)
);

-- 6. INVENTORY
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouses (id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    low_stock_threshold INTEGER NOT NULL DEFAULT 10,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (warehouse_id, product_id)
);

-- 7. INVENTORY_LOGS (AUDIT TRAIL)
CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER NOT NULL REFERENCES inventory(id) ON DELETE NO ACTION,
    change_amount INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    reason VARCHAR(50) NOT NULL, -- 'SALE', 'RESTOCK', 'ADJUSTMENT', 'RETURN'
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

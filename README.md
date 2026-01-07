# StockFlow Backend Case Study
**Solution by Varad Hajare**

## Overview
This repository contains the solution for the Backend Engineering Case Study for "StockFlow", a B2B SaaS Inventory Management System.

## Contents
1. **Code Debugging (`app.py`)**: Fixed a legacy endpoint that lacked transaction atomicity and input validation.
2. **Database Schema (`schema.sql`)**: Designed a normalized schema handling multi-warehouse inventory, bundles, and audit logs.
3. **API Implementation (`app.py`)**: Implemented a "Low Stock Alerts" endpoint with business logic for sales velocity.

## Design Decisions
* **Separation of Inventory and Products:** Necessary because products exist in multiple warehouses with different quantities.
* **Product Bundles:** Implemented as a self-referencing many-to-many relationship (`product_bundles` table).
* **Inventory Logs:** Added an audit table to track *why* inventory changes (Sale, Restock, Loss), not just the current count.
* **SKU Uniqueness:** Enforced at the database level to prevent corruption.

## Assumptions
* **Sales Data:** A `Sales` table exists to track historical data, required for calculating "days until stockout".
* **Alert Logic:** Alerts are only generated for items with "Recent Activity" (at least one sale in the last 30 days).
* **Division by Zero:** Handled by defaulting `days_until_stockout` to 999 if average daily sales is 0.

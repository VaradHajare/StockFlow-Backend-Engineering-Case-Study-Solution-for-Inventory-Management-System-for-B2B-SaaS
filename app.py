from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, Product, Inventory, Warehouse, Supplier, Sales  # Imported from models.py

app = Flask(__name__)

# ---------------------------------------------------------
# PART 1: Code Review & Debugging (Corrected Implementation)
# ---------------------------------------------------------
@app.route('/api/products', methods=['POST'])
def create_product():
    """
    Creates a new product and initializes its inventory.
    Fixes:
    - Added Atomicity (Single commit)
    - Added Input Validation
    - Added Duplicate SKU check
    """
    data = request.json
    
    # 1. Validation: Ensure required fields are present to prevent KeyErrors
    required_fields = ['name', 'sku', 'warehouse_id']
    if not all(field in data for field in required_fields):
        return {"error": "Missing required fields: name, sku, or warehouse_id"}, 400

    try:
        # 2. Duplicate Check: Enforce uniqueness before hitting the DB
        if Product.query.filter_by(sku=data['sku']).first():
            return {"error": f"Product with SKU {data['sku']} already exists"}, 409

        # 3. Create Product (Removed warehouse_id from Product model per requirements)
        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=data.get('price') 
        )
        db.session.add(product)
        db.session.flush() # Get ID without committing

        # 4. Create Initial Inventory Record
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=data.get('initial_quantity', 0)
        )
        db.session.add(inventory)

        # 5. Atomic Commit: Both Product and Inventory are saved together.
        db.session.commit()
        return {"message": "Product created", "product_id": product.id}, 201

    except Exception as e:
        db.session.rollback() # Rollback changes on any error
        return {"error": "An error occurred processing your request."}, 500


# ---------------------------------------------------------
# PART 3: API Implementation (Low Stock Alerts)
# ---------------------------------------------------------
@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    """
    Returns low stock alerts based on:
    1. Current quantity < threshold
    2. Recent sales activity (last 30 days)
    """
    alerts = []
    
    # 1. Fetch all inventory items for this company that are below threshold
    low_stock_items = db.session.query(Inventory, Product, Warehouse, Supplier).\
        join(Warehouse, Inventory.warehouse_id == Warehouse.id).\
        join(Product, Inventory.product_id == Product.id).\
        outerjoin(Supplier, Product.supplier_id == Supplier.id).\
        filter(Warehouse.company_id == company_id).\
        filter(Inventory.quantity <= Inventory.low_stock_threshold).all()

    for inv, prod, ware, supp in low_stock_items:
        
        # 2. Check for "Recent Sales Activity"
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_sales = db.session.query(func.sum(Sales.quantity_sold)).\
            filter(Sales.product_id == prod.id).\
            filter(Sales.warehouse_id == ware.id).\
            filter(Sales.sold_at >= thirty_days_ago).scalar() or 0
            
        # If no recent sales, skip alerting
        if recent_sales == 0:
            continue

        # 3. Calculate Days Until Stockout
        avg_daily_sales = recent_sales / 30.0
        
        # Edge Case: Avoid division by zero
        if avg_daily_sales > 0:
            days_until_stockout = int(inv.quantity / avg_daily_sales)
        else:
            days_until_stockout = 999 

        # 4. Construct Response Object
        alert_obj = {
            "product_id": prod.id,
            "product_name": prod.name,
            "sku": prod.sku,
            "warehouse_id": ware.id,
            "warehouse_name": ware.name,
            "current_stock": inv.quantity,
            "threshold": inv.low_stock_threshold,
            "days_until_stockout": days_until_stockout,
            "supplier": {
                # Edge Case: Handle missing supplier
                "id": supp.id if supp else None,
                "name": supp.name if supp else "Unknown",
                "contact_email": supp.contact_email if supp else None
            }
        }
        alerts.append(alert_obj)

    response = {
        "alerts": alerts,
        "total_alerts": len(alerts)
    }
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)

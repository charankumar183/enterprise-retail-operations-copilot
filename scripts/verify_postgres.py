import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.app.database import engine, SessionLocal
from backend.app.models.retail import (
    Product, Inventory, SalesTransaction, PurchaseOrder, Supplier, Customer,
    Promotion, Store, Warehouse, Shipment, ProductReturn, PricingHistory,
    DemandForecast, Employee
)
from backend.app.models.auth import User
from sqlalchemy import inspect

def verify_postgresql():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Database Connection: SUCCESS")
    print(f"Total Tables in Database: {len(tables)}")

    db = SessionLocal()
    entities = [
        ("1. Product Master", Product),
        ("2. Inventory", Inventory),
        ("3. Sales Transactions", SalesTransaction),
        ("4. Purchase Orders", PurchaseOrder),
        ("5. Suppliers", Supplier),
        ("6. Customers", Customer),
        ("7. Promotions", Promotion),
        ("8. Stores", Store),
        ("9. Warehouses", Warehouse),
        ("10. Shipments", Shipment),
        ("11. Returns", ProductReturn),
        ("12. Pricing History", PricingHistory),
        ("13. Demand Forecast", DemandForecast),
        ("14. Employee Info", Employee),
        ("15. Auth Users", User)
    ]

    print("\n--- ENTITY RECORD COUNTS ---")
    for name, model in entities:
        cnt = db.query(model).count()
        print(f"{name:25s}: {cnt:4d} rows")

    print("\n--- VERIFYING CORE QUERIES ON POSTGRESQL ---")
    # 1. Product & Inventory
    p = db.query(Product).filter(Product.product_id == "P100").first()
    print(f"Product Query: Found SKU {p.product_id} -> {p.name} (${p.unit_price})")
    inv_rows = db.query(Inventory).filter(Inventory.product_id == "P100").all()
    print(f"Inventory Query: {len(inv_rows)} stock locations found for P100")
    for row in inv_rows:
        print(f"  - Location {row.location_id} ({row.location_type}): {row.quantity_on_hand} on hand")

    # 2. Sales Query
    sales_cnt = db.query(SalesTransaction).count()
    recent_sale = db.query(SalesTransaction).first()
    print(f"Sales Query: Total {sales_cnt} transactions; First: TXN {recent_sale.transaction_id} (${recent_sale.total_amount})")

    # 3. Supplier & PO Query
    delayed_pos = db.query(PurchaseOrder).filter(PurchaseOrder.status == "delayed").all()
    print(f"Supplier/PO Query: Found {len(delayed_pos)} delayed POs")
    for po in delayed_pos:
        print(f"  - PO {po.po_number} from Supplier {po.supplier_id} -> Destination {po.destination_warehouse_id}")

    # 4. Primary & Foreign Key Check
    print("\n--- VERIFYING FOREIGN KEY CONSTRAINTS ---")
    for t in ["products", "inventories", "purchase_orders", "returns", "shipments", "employees"]:
        fks = inspector.get_foreign_keys(t)
        fk_summary = [f"{fk['referred_table']}.{fk['referred_columns'][0]}" for fk in fks]
        print(f"Table {t:16s} FKs: {fk_summary}")

    db.close()

if __name__ == "__main__":
    verify_postgresql()

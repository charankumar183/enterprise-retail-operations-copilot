from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.retail import Inventory, Product, Warehouse, Store
from backend.app.schemas.retail import InventoryItem, InventoryOverview
from backend.app.services.sql_analytics import SQLAnalyticsService

router = APIRouter(prefix="/inventory", tags=["Inventory Operations"])

@router.get("/overview", response_model=InventoryOverview)
def get_inventory_overview(db: Session = Depends(get_db)):
    """Executive Inventory Dashboard overview with stock health metrics and cross-facility totals."""
    items = db.query(Inventory).all()
    products_count = db.query(Product).count()
    wh_count = db.query(Warehouse).count()
    stores_count = db.query(Store).count()

    low_stock = sum(1 for i in items if i.status == "Low Stock")
    out_of_stock = sum(1 for i in items if i.status == "Out of Stock" or i.quantity_on_hand == 0)

    # Join product names
    inventory_items = []
    prod_map = {p.product_id: p.name for p in db.query(Product).all()}

    for item in items:
        inventory_items.append(InventoryItem(
            product_id=item.product_id,
            product_name=prod_map.get(item.product_id, "Unknown Product"),
            location_type=item.location_type,
            location_id=item.location_id,
            quantity_on_hand=item.quantity_on_hand,
            quantity_reserved=item.quantity_reserved,
            reorder_threshold=item.reorder_threshold,
            safety_stock=item.safety_stock,
            status=item.status
        ))

    return InventoryOverview(
        total_products=products_count,
        low_stock_count=low_stock,
        out_of_stock_count=out_of_stock,
        warehouses_active=wh_count,
        stores_active=stores_count,
        inventory_items=inventory_items
    )

@router.get("/lookup/{product_id}")
def lookup_product_inventory(product_id: str, db: Session = Depends(get_db)):
    """Inventory lookup across all warehouses and stores for Product X / P100."""
    analytics = SQLAnalyticsService(db)
    result = analytics.get_inventory_availability(product_id)
    return result

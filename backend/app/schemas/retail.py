from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    product_id: str
    name: str
    category: str
    department: str
    brand: str
    unit_price: float
    cost_price: float
    supplier_id: str
    min_reorder_level: int
    lead_time_days: int
    description: Optional[str] = None

class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class InventoryItem(BaseModel):
    product_id: str
    product_name: Optional[str] = None
    location_type: str
    location_id: str
    quantity_on_hand: int
    quantity_reserved: int
    reorder_threshold: int
    safety_stock: int
    status: str

    class Config:
        from_attributes = True

class InventoryOverview(BaseModel):
    total_products: int
    low_stock_count: int
    out_of_stock_count: int
    warehouses_active: int
    stores_active: int
    inventory_items: List[InventoryItem]

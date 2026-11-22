from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

# 1. Product Master
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. 'P100', 'P-ABC', 'PROD-101'
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True) # Electronics, Grocery, Apparel, Home Goods
    department = Column(String(100), nullable=False, index=True)
    brand = Column(String(100), nullable=False)
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    supplier_id = Column(String(50), ForeignKey("suppliers.supplier_id"), nullable=False, index=True)
    min_reorder_level = Column(Integer, default=50)
    lead_time_days = Column(Integer, default=7)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="products")
    inventories = relationship("Inventory", back_populates="product")
    sales = relationship("SalesTransaction", back_populates="product")
    returns = relationship("ProductReturn", back_populates="product")
    pricing_histories = relationship("PricingHistory", back_populates="product")
    forecasts = relationship("DemandForecast", back_populates="product")


# 2. Suppliers
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. 'SUP-XYZ', 'SUP-ABC'
    name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(50))
    category = Column(String(100))
    reliability_score = Column(Float, default=0.95) # 0.0 - 1.0
    lead_time_days = Column(Integer, default=5)
    status = Column(String(50), default="active") # active, on_hold, inactive

    products = relationship("Product", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


# 3. Store Information
class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. 'STORE-105', 'STORE-210'
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    region = Column(String(50), nullable=False, index=True) # North, South, East, West, Midwest
    store_type = Column(String(50), default="Supermarket") # Supercenter, Express, Hypermarket
    manager_name = Column(String(100))
    daily_sales_target = Column(Float, default=25000.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    employees = relationship("Employee", back_populates="store")
    sales = relationship("SalesTransaction", back_populates="store")
    returns = relationship("ProductReturn", back_populates="store")


# 4. Warehouse Information
class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. 'WH-001', 'WH-CENTRAL'
    name = Column(String(255), nullable=False)
    location = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False, index=True)
    capacity_sqft = Column(Integer, default=250000)
    utilization_pct = Column(Float, default=78.5)
    manager_name = Column(String(100))


# 5. Inventory
class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True, nullable=False)
    location_type = Column(String(50), nullable=False, index=True) # 'warehouse' or 'store'
    location_id = Column(String(50), nullable=False, index=True) # WH-001, STORE-105
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    quantity_reserved = Column(Integer, default=0, nullable=False)
    reorder_threshold = Column(Integer, default=50, nullable=False)
    safety_stock = Column(Integer, default=20, nullable=False)
    last_replenished = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="In Stock") # 'In Stock', 'Low Stock', 'Out of Stock'

    product = relationship("Product", back_populates="inventories")


# 6. Customers
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(120), unique=True, index=True)
    phone = Column(String(50))
    segment = Column(String(50), default="Retail") # Retail, Wholesale, Premium
    loyalty_tier = Column(String(50), default="Silver") # Bronze, Silver, Gold, Platinum
    created_at = Column(DateTime, default=datetime.utcnow)

    sales = relationship("SalesTransaction", back_populates="customer")


# 7. Sales Transactions
class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, index=True, nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id"), index=True, nullable=False)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), default="Credit Card") # Credit Card, Debit Card, Cash, UPI
    transaction_date = Column(DateTime, default=datetime.utcnow, index=True)

    product = relationship("Product", back_populates="sales")
    store = relationship("Store", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")


# 8. Purchase Orders
class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, index=True, nullable=False) # e.g. 'PO-9001'
    supplier_id = Column(String(50), ForeignKey("suppliers.supplier_id"), index=True, nullable=False)
    destination_warehouse_id = Column(String(50), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, index=True)
    expected_delivery_date = Column(DateTime, nullable=False)
    actual_delivery_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending", index=True) # pending, confirmed, shipped, delivered, delayed, cancelled
    total_cost = Column(Float, default=0.0)
    items_count = Column(Integer, default=1)
    notes = Column(Text, nullable=True)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    shipments = relationship("Shipment", back_populates="purchase_order")


# 9. Promotions
class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(50), unique=True, index=True, nullable=False)
    campaign_name = Column(String(150), nullable=False)
    product_category = Column(String(100), nullable=False, index=True)
    discount_percentage = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    policy_version = Column(String(20), default="v1.0") # e.g. "Version 3", "Version 5"
    status = Column(String(50), default="active") # active, scheduled, expired
    terms = Column(Text, nullable=True)


# 10. Shipments
class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String(50), unique=True, index=True, nullable=False)
    po_number = Column(String(50), ForeignKey("purchase_orders.po_number"), index=True, nullable=True)
    origin_type = Column(String(50), nullable=False) # Supplier, Warehouse
    origin_id = Column(String(50), nullable=False)
    destination_type = Column(String(50), nullable=False) # Warehouse, Store
    destination_id = Column(String(50), nullable=False)
    carrier = Column(String(100), default="FedEx Freight")
    tracking_number = Column(String(100), unique=True)
    status = Column(String(50), default="In Transit") # Manifested, In Transit, Delivered, Delayed
    shipped_date = Column(DateTime, default=datetime.utcnow)
    estimated_delivery = Column(DateTime, nullable=False)
    actual_delivery = Column(DateTime, nullable=True)

    purchase_order = relationship("PurchaseOrder", back_populates="shipments")


# 11. Returns
class ProductReturn(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(String(50), unique=True, index=True, nullable=False)
    transaction_id = Column(String(50), index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True, nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id"), index=True, nullable=False)
    customer_id = Column(String(50), nullable=True)
    reason = Column(String(255), nullable=False) # Defective, Wrong Size, Buyer Remorse, Damaged in Box
    quantity = Column(Integer, default=1)
    refund_amount = Column(Float, nullable=False)
    return_date = Column(DateTime, default=datetime.utcnow, index=True)
    condition = Column(String(50), default="Defective") # Restockable, Defective, Disposed

    product = relationship("Product", back_populates="returns")
    store = relationship("Store", back_populates="returns")


# 12. Pricing History
class PricingHistory(Base):
    __tablename__ = "pricing_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True, nullable=False)
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    effective_date = Column(DateTime, default=datetime.utcnow, index=True)
    change_reason = Column(String(255), nullable=False) # Seasonal Markdown, Cost Increase, Competitor Match
    approved_by = Column(String(100), default="Category Director")

    product = relationship("Product", back_populates="pricing_histories")


# 13. Demand Forecast
class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True, nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id"), index=True, nullable=False)
    forecast_date = Column(Date, nullable=False, index=True)
    predicted_demand = Column(Integer, nullable=False)
    actual_demand = Column(Integer, nullable=True)
    confidence_interval_low = Column(Integer, nullable=False)
    confidence_interval_high = Column(Integer, nullable=False)
    variance_pct = Column(Float, default=0.0)

    product = relationship("Product", back_populates="forecasts")


# 14. Employee Information
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False) # Store Associate, Assistant Manager, Inventory Specialist
    store_id = Column(String(50), ForeignKey("stores.store_id"), index=True, nullable=False)
    department = Column(String(100), nullable=False)
    shift = Column(String(50), default="Morning") # Morning, Evening, Night
    performance_rating = Column(Float, default=4.2) # 1.0 to 5.0
    status = Column(String(50), default="Active")

    store = relationship("Store", back_populates="employees")

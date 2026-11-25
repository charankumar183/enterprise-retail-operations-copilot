from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True); email=Column(String(160),unique=True,nullable=False); password_hash=Column(String(255),nullable=False); role=Column(String(40),nullable=False,default='Store Manager'); active=Column(Boolean,default=True)
class Product(Base):
    __tablename__='products'
    id=Column(Integer,primary_key=True); sku=Column(String(40),unique=True,index=True); name=Column(String(180)); category=Column(String(80)); price=Column(Float); supplier_id=Column(Integer,ForeignKey('suppliers.id'))
class Supplier(Base):
    __tablename__='suppliers'
    id=Column(Integer,primary_key=True); name=Column(String(120)); region=Column(String(80)); contact=Column(String(140))
class Store(Base):
    __tablename__='stores'
    id=Column(Integer,primary_key=True); code=Column(String(25),unique=True); name=Column(String(120)); region=Column(String(80))
class Warehouse(Base):
    __tablename__='warehouses'
    id=Column(Integer,primary_key=True); code=Column(String(30),unique=True); name=Column(String(120)); region=Column(String(80))
class Inventory(Base):
    __tablename__='inventory'; __table_args__=(UniqueConstraint('product_id','warehouse_id','store_id',name='uq_inventory_location'),)
    id=Column(Integer,primary_key=True); product_id=Column(Integer,ForeignKey('products.id')); warehouse_id=Column(Integer,ForeignKey('warehouses.id'),nullable=True); store_id=Column(Integer,ForeignKey('stores.id'),nullable=True); quantity=Column(Integer); reorder_point=Column(Integer)
class Sale(Base):
    __tablename__='sales'; id=Column(Integer,primary_key=True); product_id=Column(Integer,ForeignKey('products.id')); store_id=Column(Integer,ForeignKey('stores.id')); quantity=Column(Integer); unit_price=Column(Float); sold_at=Column(DateTime)
class PurchaseOrder(Base):
    __tablename__='purchase_orders'; id=Column(Integer,primary_key=True); po_number=Column(String(45),unique=True); supplier_id=Column(Integer,ForeignKey('suppliers.id')); product_id=Column(Integer,ForeignKey('products.id')); warehouse_id=Column(Integer,ForeignKey('warehouses.id')); quantity=Column(Integer); status=Column(String(30)); expected_at=Column(DateTime); created_at=Column(DateTime,server_default=func.now())
class Customer(Base):
    __tablename__='customers'; id=Column(Integer,primary_key=True); customer_code=Column(String(35),unique=True); segment=Column(String(40)); region=Column(String(40))
class Promotion(Base):
    __tablename__='promotions'; id=Column(Integer,primary_key=True); campaign=Column(String(120)); product_id=Column(Integer,ForeignKey('products.id')); discount_pct=Column(Float); starts_at=Column(DateTime); ends_at=Column(DateTime)
class Shipment(Base):
    __tablename__='shipments'; id=Column(Integer,primary_key=True); po_id=Column(Integer,ForeignKey('purchase_orders.id')); status=Column(String(30)); tracking_id=Column(String(60)); delivered_at=Column(DateTime)
class Return(Base):
    __tablename__='returns'; id=Column(Integer,primary_key=True); product_id=Column(Integer,ForeignKey('products.id')); store_id=Column(Integer,ForeignKey('stores.id')); quantity=Column(Integer); reason=Column(String(120)); returned_at=Column(DateTime)
class PricingHistory(Base):
    __tablename__='pricing_history'; id=Column(Integer,primary_key=True); product_id=Column(Integer,ForeignKey('products.id')); previous_price=Column(Float); price=Column(Float); effective_at=Column(DateTime)
class DemandForecast(Base):
    __tablename__='demand_forecasts'; id=Column(Integer,primary_key=True); product_id=Column(Integer,ForeignKey('products.id')); store_id=Column(Integer,ForeignKey('stores.id')); forecast_units=Column(Integer); period=Column(String(15))
class Employee(Base):
    __tablename__='employees'; id=Column(Integer,primary_key=True); employee_code=Column(String(35)); store_id=Column(Integer,ForeignKey('stores.id')); department=Column(String(70)); role=Column(String(70))
class Complaint(Base):
    __tablename__='complaints'; id=Column(Integer,primary_key=True); product_id=Column(Integer,ForeignKey('products.id')); customer_id=Column(Integer,ForeignKey('customers.id')); complaint=Column(Text); opened_at=Column(DateTime)
class Document(Base):
    __tablename__='documents'; id=Column(Integer,primary_key=True); name=Column(String(255)); path=Column(String(1000)); doc_type=Column(String(50)); department=Column(String(80)); region=Column(String(80)); version=Column(String(40)); product_category=Column(String(80),default=''); store_code=Column(String(40),default=''); warehouse_code=Column(String(40),default=''); supplier_code=Column(String(80),default=''); promotion_campaign=Column(String(80),default=''); effective_date=Column(String(30),default=''); file_hash=Column(String(64)); indexed=Column(Boolean,default=False); created_at=Column(DateTime,server_default=func.now())
class ChatMessage(Base):
    __tablename__='chat_messages'; id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id')); session_id=Column(String(70),index=True); role=Column(String(12)); content=Column(Text); created_at=Column(DateTime,server_default=func.now())
class Report(Base):
    __tablename__='reports'; id=Column(Integer,primary_key=True); title=Column(String(200)); kind=Column(String(50)); file_path=Column(String(1000)); user_id=Column(Integer,ForeignKey('users.id')); created_at=Column(DateTime,server_default=func.now())
class Feedback(Base):
    __tablename__='feedback'; id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id')); question=Column(Text); rating=Column(Integer); comment=Column(Text); created_at=Column(DateTime,server_default=func.now())
class AuditLog(Base):
    __tablename__='audit_logs'; id=Column(Integer,primary_key=True); user_id=Column(Integer,nullable=True); action=Column(String(100)); details=Column(Text); duration_ms=Column(Float,nullable=True); created_at=Column(DateTime,server_default=func.now())

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.models import Base,Product,Store,Warehouse,Inventory,Supplier,Sale,Return,PurchaseOrder
from app.analytics import analyze,dashboard
from datetime import datetime,timedelta

def memory_db():
    eng=create_engine('sqlite+pysqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(eng)
    db=Session(eng)
    s=Supplier(name='Sample Supplier',region='North',contact='demo@example.test');st=Store(code='210',name='Store 210',region='South');wh=Warehouse(code='WH-1',name='Warehouse',region='North')
    db.add_all([s,st,wh]);db.flush()
    p=Product(sku='P100',name='Sample Grocery',category='Grocery',price=15,supplier_id=s.id);db.add(p);db.flush()
    db.add_all([Inventory(product_id=p.id,warehouse_id=wh.id,quantity=8,reorder_point=35),Inventory(product_id=p.id,store_id=st.id,quantity=4,reorder_point=20),Sale(product_id=p.id,store_id=st.id,quantity=20,unit_price=15,sold_at=datetime.now()),Return(product_id=p.id,store_id=st.id,quantity=2,reason='Damaged',returned_at=datetime.now())]);db.commit()
    return db

def test_inventory_lookup():
    db=memory_db();rows=analyze(db,'Show inventory for Product P100 across warehouses');assert rows and rows[0]['sku']=='P100';db.close()

def test_return_rate():
    db=memory_db();rows=analyze(db,'Which products have highest return rate');assert rows[0]['return_rate_percent']==10;db.close()

def test_supplier():
    db=memory_db();rows=analyze(db,'Who is the supplier for Product P100?');assert rows[0]['supplier']=='Sample Supplier';db.close()

def test_dashboard_aggregate():
    db=memory_db();result=dashboard(db);assert result['products']==1 and result['low_stock_locations']==2;db.close()

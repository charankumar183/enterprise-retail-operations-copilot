import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import *
from .auth import hash_password, ROLES

CATEGORIES=['Grocery','Electronics','Apparel','Personal Care','Home & Kitchen','Beverages']
NAMES=['Rice','Olive Oil','Headphones','T-Shirt','Shampoo','Coffee','Detergent','Backpack','Juice','Sneakers','Tea','Cereal','Soap','Tablet','Jacket','Lamp','Pasta','Milk','Towel','Biscuits']

def seed(db:Session):
    if db.scalar(select(User.id).limit(1)): return False
    rng=random.Random(2026); now=datetime.now(timezone.utc).replace(tzinfo=None)
    for n,role in enumerate(ROLES):
        email=('admin' if role=='Administrator' else role.lower().replace(' ','_'))+'@demo.retail'
        db.add(User(email=email,role=role,password_hash=hash_password('RetailDemo2026!')))
    suppliers=[Supplier(name=f'Supplier {n:02d} Logistics',region=['North','South','East','West'][n%4],contact=f'vendor{n}@example.test') for n in range(1,26)]
    stores=[Store(code=str(code),name=f'Store {code}',region=['North','South','West','East'][i%4]) for i,code in enumerate([105,210,305,410,515])]
    warehouses=[Warehouse(code=f'WH-{i}',name=f'Warehouse {i}',region=['North','South','West','East'][i-1]) for i in range(1,5)]
    db.add_all(suppliers+stores+warehouses); db.flush()
    products=[]
    for n in range(1,121):
        p=Product(sku=f'P{n:03d}',name=f'{NAMES[(n-1)%len(NAMES)]} {n:03d}',category=CATEGORIES[(n-1)%6],price=float(rng.randint(8,299)),supplier_id=suppliers[n%len(suppliers)].id)
        products.append(p)
    db.add_all(products);db.flush()
    for p in products:
        for wh in warehouses:
            q=rng.randint(0,220)
            if p.sku=='P100': q=rng.randint(0,12)
            db.add(Inventory(product_id=p.id,warehouse_id=wh.id,quantity=q,reorder_point=35))
        for st in stores:
            q=rng.randint(0,100);q=(rng.randint(0,7) if p.sku=='P100' else q)
            db.add(Inventory(product_id=p.id,store_id=st.id,quantity=q,reorder_point=20))
            db.add(DemandForecast(product_id=p.id,store_id=st.id,forecast_units=rng.randint(10,100),period=now.strftime('%Y-%m')))
        db.add(PricingHistory(product_id=p.id,previous_price=p.price*1.1,price=p.price,effective_at=now-timedelta(days=25)))
    for i in range(800):
        p=products[rng.randrange(len(products))];st=stores[rng.randrange(len(stores))]
        db.add(Sale(product_id=p.id,store_id=st.id,quantity=rng.randint(1,8),unit_price=p.price,sold_at=now-timedelta(days=rng.randint(0,29))))
    for i in range(160):
        p=products[rng.randrange(len(products))];st=stores[rng.randrange(len(stores))]
        db.add(Return(product_id=p.id,store_id=st.id,quantity=rng.randint(1,3),reason=rng.choice(['Damaged','Wrong size','Quality issue','Customer preference']),returned_at=now-timedelta(days=rng.randint(0,29))))
    for i in range(100):
        p=products[i%len(products)];s=suppliers[i%len(suppliers)];wh=warehouses[i%len(warehouses)]
        expected=now+timedelta(days=rng.randint(-18,16));status=('Delayed' if expected<now else rng.choice(['Open','In transit','Received']))
        po=PurchaseOrder(po_number=f'PO-{i+1:05d}',supplier_id=s.id,product_id=p.id,warehouse_id=wh.id,quantity=rng.randint(15,250),status=status,expected_at=expected)
        db.add(po);db.flush()
        db.add(Shipment(po_id=po.id,status='Late' if status=='Delayed' else 'Scheduled',tracking_id=f'TRK-{i+1000}',delivered_at=None))
    for i in range(80):
        p=products[i%len(products)]
        db.add(Promotion(campaign=f'Promo Campaign {i%12+1}',product_id=p.id,discount_pct=rng.randint(5,25),starts_at=now-timedelta(days=3),ends_at=now+timedelta(days=10)))
    customers=[]
    for i in range(1,61): customers.append(Customer(customer_code=f'C{i:05d}',segment=rng.choice(['Retail','Premium','Wholesale']),region=rng.choice(['North','South','West','East'])))
    db.add_all(customers);db.flush()
    for i in range(90):
        p=products[i%len(products)];c=customers[i%len(customers)]
        db.add(Complaint(product_id=p.id,customer_id=c.id,complaint=rng.choice(['Packaging arrived damaged','Delivery was later than promised','Wrong color received','Product performance below expectation']),opened_at=now-timedelta(days=rng.randint(0,29))))
    for i in range(48):db.add(Employee(employee_code=f'E{i+1:05d}',store_id=stores[i%len(stores)].id,department=rng.choice(['Receiving','Merchandising','Customer Service','Logistics']),role='Associate'))
    db.commit();return True

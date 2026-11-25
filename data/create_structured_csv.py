"""Portable synthetic CSV snapshots. PostgreSQL itself is initialized by app.seed."""
import csv,random
from pathlib import Path
from datetime import datetime,timedelta
BASE=Path(__file__).parent/'structured';BASE.mkdir(exist_ok=True)
r=random.Random(2026)

def write(name,columns,rows):
    with (BASE/name).open('w',newline='',encoding='utf8') as f:
        w=csv.writer(f);w.writerow(columns);w.writerows(rows)

cats=['Grocery','Electronics','Apparel','Personal Care','Home & Kitchen','Beverages']
items=['Rice','Olive Oil','Headphones','T-Shirt','Shampoo','Coffee','Detergent','Backpack','Juice','Sneakers','Tea','Cereal','Soap','Tablet','Jacket','Lamp','Pasta','Milk','Towel','Biscuits']
now=datetime(2026,11,21)
products=[(i,f'P{i:03d}',f'{items[(i-1)%20]} {i:03d}',cats[(i-1)%6],r.randint(8,299),(i%25)+1) for i in range(1,121)]
write('product_master.csv',['id','sku','name','category','price','supplier_id'],products)
write('suppliers.csv',['id','name','region','contact'],[(i,f'Supplier {i:02d} Logistics',['North','South','East','West'][(i-1)%4],f'vendor{i}@example.test') for i in range(1,26)])
write('stores.csv',['id','code','name','region'],[(i,str(code),f'Store {code}',['North','South','West','East'][(i-1)%4]) for i,code in enumerate([105,210,305,410,515],1)])
write('warehouses.csv',['id','code','name','region'],[(i,f'WH-{i}',f'Warehouse {i}',['North','South','West','East'][i-1]) for i in range(1,5)])
inv=[];forecasts=[]
for i,p in enumerate(products,1):
 for w in range(1,5):inv.append((len(inv)+1,i,w,'',r.randint(0,12) if i==100 else r.randint(0,220),35))
 for st in range(1,6):
  inv.append((len(inv)+1,i,'',st,r.randint(0,7) if i==100 else r.randint(0,100),20))
  forecasts.append((len(forecasts)+1,i,st,r.randint(10,100),'2026-11'))
write('inventory.csv',['id','product_id','warehouse_id','store_id','quantity','reorder_point'],inv)
write('demand_forecast.csv',['id','product_id','store_id','forecast_units','period'],forecasts)
write('sales_transactions.csv',['id','product_id','store_id','quantity','unit_price','sold_at'],[(i,pid:=r.randint(1,120),r.randint(1,5),r.randint(1,8),products[pid-1][4],(now-timedelta(days=r.randint(0,29))).isoformat()) for i in range(1,801)])
write('returns.csv',['id','product_id','store_id','quantity','reason','returned_at'],[(i,r.randint(1,120),r.randint(1,5),r.randint(1,3),r.choice(['Damaged','Wrong size','Quality issue','Customer preference']),(now-timedelta(days=r.randint(0,29))).isoformat()) for i in range(1,161)])
write('purchase_orders.csv',['id','po_number','supplier_id','product_id','warehouse_id','quantity','status','expected_at'],[(i,f'PO-{i:05d}',(i%25)+1,(i%120)+1,(i%4)+1,r.randint(15,250),'Delayed' if i%4==0 else 'Open',(now+timedelta(days=-4 if i%4==0 else 12)).isoformat()) for i in range(1,101)])
write('shipments.csv',['id','purchase_order_id','status','tracking_id'],[(i,i,'Late' if i%4==0 else 'Scheduled',f'TRK-{i+1000}') for i in range(1,101)])
write('customers.csv',['id','customer_code','segment','region'],[(i,f'C{i:05d}',r.choice(['Retail','Premium','Wholesale']),r.choice(['North','South','West','East'])) for i in range(1,61)])
write('promotions.csv',['id','campaign','product_id','discount_pct','starts_at','ends_at'],[(i,f'Promo Campaign {i%12+1}',i,r.randint(5,25),'2026-11-18','2026-12-01') for i in range(1,81)])
write('pricing_history.csv',['id','product_id','previous_price','price','effective_at'],[(i,i,round(p[4]*1.1,2),p[4],'2026-11-01') for i,p in enumerate(products,1)])
write('employees.csv',['id','employee_code','store_id','department','role'],[(i,f'E{i:05d}',i%5+1,r.choice(['Receiving','Merchandising','Customer Service','Logistics']),'Associate') for i in range(1,49)])
write('complaints.csv',['id','product_id','customer_id','complaint','opened_at'],[(i,i%120+1,i%60+1,r.choice(['Damaged packaging','Delayed delivery','Wrong color','Quality complaint']),'2026-11-15') for i in range(1,91)])
print('Generated 15 structured CSV snapshots. Synthetic snapshots are illustrative; database seed is authoritative at runtime.')

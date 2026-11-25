"""Constrained SQL analytics: ORM/parameterized queries only, no free-form LLM SQL execution."""
from sqlalchemy import func,select
from datetime import datetime,timedelta
from .models import Product,Inventory,Store,Warehouse,Sale,PurchaseOrder,Supplier,Return,Complaint,DemandForecast

def route_intent(text):
    q=text.lower()
    if any(w in q for w in ['report','daily operations','checklist','replenishment']):return 'report'
    if any(w in q for w in ['procedure','policy','manual','guideline','contract','sop','compare promotion']):return 'rag'
    if any(w in q for w in ['inventory','stock','available','warehouse','supplier','vendor','purchase order','po-','sales','return rate','highest return','delayed','forecast','complaint','product p']):return 'sql'
    return 'rag'

def analyze(db,question):
    q=question.lower();import re
    code_match=re.search(r'\b[Pp](\d{3})\b',question)
    prod= db.scalar(select(Product).where(Product.sku==f'P{code_match.group(1)}')) if code_match else None
    store_match=re.search(r'store\s+(\d+)',q)
    store=db.scalar(select(Store).where(Store.code==store_match.group(1))) if store_match else None
    if 'compare' in q and len(re.findall(r'\bP\d{3}\b',question,re.I))>=2:
        skus=[x.upper() for x in re.findall(r'\bP\d{3}\b',question,re.I)]
        records=db.scalars(select(Product).where(Product.sku.in_(skus))).all()
        result=[]
        for p in records:
            stock=db.scalar(select(func.sum(Inventory.quantity)).where(Inventory.product_id==p.id)) or 0
            sup=db.get(Supplier,p.supplier_id)
            result.append({'sku':p.sku,'name':p.name,'category':p.category,'price':p.price,'supplier':sup.name if sup else None,'total_stock':int(stock)})
        return result
    if any(x in q for x in ['highest return','return rate','most returned']):
        sales_query=select(Sale.product_id,func.sum(Sale.quantity))
        returns_query=select(Return.product_id,func.sum(Return.quantity))
        if 'this month' in q:
            now=datetime.utcnow();start=now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
            sales_query=sales_query.where(Sale.sold_at>=start)
            returns_query=returns_query.where(Return.returned_at>=start)
        sales=dict(db.execute(sales_query.group_by(Sale.product_id)).all())
        returns=db.execute(returns_query.group_by(Return.product_id)).all()
        ordered=sorted([(pid,qty,round(100*qty/max(1,sales.get(pid,0)),2)) for pid,qty in returns],key=lambda v:v[2],reverse=True)[:10]
        names=dict(db.execute(select(Product.id,Product.name)).all())
        return [{'product':names.get(pid),'returned_units':qty,'return_rate_percent':rate} for pid,qty,rate in ordered]
    if 'delayed' in q and ('order' in q or 'po' in q):
        stmt=select(PurchaseOrder.po_number,Supplier.name,PurchaseOrder.quantity,PurchaseOrder.expected_at).join(Supplier,PurchaseOrder.supplier_id==Supplier.id).where(PurchaseOrder.status=='Delayed')
        match=re.search(r'supplier\s+([a-z0-9]+)',q)
        if match and match.group(1) not in {'xyz','abc'}:stmt=stmt.where(Supplier.name.ilike(f'%Supplier {match.group(1)}%'))
        stmt=stmt.order_by(PurchaseOrder.expected_at).limit(20)
        return [{'purchase_order':n,'supplier':s,'quantity':qty,'expected_at':date.date().isoformat()} for n,s,qty,date in db.execute(stmt)]
    if 'supplier' in q or 'vendor' in q:
        stmt=select(Product.sku,Product.name,Supplier.name).join(Supplier,Product.supplier_id==Supplier.id)
        if prod:stmt=stmt.where(Product.id==prod.id)
        return [{'sku':sku,'product':name,'supplier':supp} for sku,name,supp in db.execute(stmt.limit(20))]
    if 'complaint' in q:
        stmt=select(Product.sku,Complaint.complaint).join(Product,Complaint.product_id==Product.id)
        if prod:stmt=stmt.where(Product.id==prod.id)
        return [{'product':sku,'complaint':text} for sku,text in db.execute(stmt.limit(15))]
    if 'sales' in q:
        stmt=select(Product.sku,func.sum(Sale.quantity),func.sum(Sale.quantity*Sale.unit_price)).join(Product,Sale.product_id==Product.id).group_by(Product.sku).order_by(func.sum(Sale.quantity*Sale.unit_price).desc()).limit(15)
        if prod:stmt=stmt.where(Product.id==prod.id)
        return [{'sku':s,'units_sold':int(u),'revenue':round(float(v),2)} for s,u,v in db.execute(stmt)]
    if 'forecast' in q:
        stmt=select(Product.sku,func.sum(DemandForecast.forecast_units)).join(Product,Product.id==DemandForecast.product_id).group_by(Product.sku).limit(20)
        if prod:stmt=stmt.where(Product.id==prod.id)
        return [{'sku':sku,'forecast_units':int(units)} for sku,units in db.execute(stmt)]
    if any(x in q for x in ['inventory','stock','available','warehouse','replenishment']) or prod or store:
        stmt=select(Product.sku,Product.name,Inventory.quantity,Inventory.reorder_point,Warehouse.code,Store.code).join(Product,Inventory.product_id==Product.id).outerjoin(Warehouse,Inventory.warehouse_id==Warehouse.id).outerjoin(Store,Inventory.store_id==Store.id)
        if prod:stmt=stmt.where(Product.id==prod.id)
        if store:stmt=stmt.where(Inventory.store_id==store.id)
        elif 'warehouse' in q and 'store' not in q:stmt=stmt.where(Inventory.warehouse_id.is_not(None))
        stmt=stmt.order_by(Inventory.quantity).limit(60)
        return [{'sku':sku,'product':name,'quantity':qty,'reorder_point':rp,'location':(wh or f'Store {st}'),'low_stock':qty<rp} for sku,name,qty,rp,wh,st in db.execute(stmt)]
    return None

def dashboard(db):
    total=db.scalar(select(func.count(Product.id))) or 0
    warehouses=db.scalar(select(func.count(Warehouse.id))) or 0
    stores=db.scalar(select(func.count(Store.id))) or 0
    low=db.scalar(select(func.count(Inventory.id)).where(Inventory.quantity<Inventory.reorder_point)) or 0
    revenue=db.scalar(select(func.sum(Sale.quantity*Sale.unit_price))) or 0
    by_cat=db.execute(select(Product.category,func.count(Product.id)).group_by(Product.category)).all()
    low_items=db.execute(select(Product.sku,Product.name,Inventory.quantity,Inventory.reorder_point).join(Inventory,Product.id==Inventory.product_id).where(Inventory.quantity<Inventory.reorder_point).order_by(Inventory.quantity).limit(10)).all()
    return {'products':total,'warehouses':warehouses,'stores':stores,'low_stock_locations':low,'sales_revenue':round(float(revenue),2),'categories':[{'category':c,'count':n} for c,n in by_cat],'low_stock_items':[{'sku':sku,'product':name,'quantity':q,'reorder_point':rp} for sku,name,q,rp in low_items]}

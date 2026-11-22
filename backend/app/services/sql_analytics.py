import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from backend.app.models.retail import (
    Product, Inventory, Warehouse, Store, Supplier,
    PurchaseOrder, SalesTransaction, ProductReturn, DemandForecast
)

class SQLAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def execute_custom_sql(self, query: str) -> List[Dict[str, Any]]:
        """Safe execution of read-only analytics queries."""
        clean_q = query.strip()
        # Verify read-only
        if not re.match(r'^(SELECT|WITH)\b', clean_q, re.IGNORECASE):
            raise ValueError("Only read-only SELECT queries are allowed in SQL analytics.")
        
        result = self.db.execute(text(clean_q))
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def get_inventory_availability(self, product_identifier: str) -> Dict[str, Any]:
        """Show inventory availability for Product X across all warehouses and stores."""
        clean_id = product_identifier.strip().upper()
        if clean_id in ["X", "PRODUCT X", "PRODUCT-X"]:
            target_id = "PRODUCT-X"
        elif clean_id in ["Y", "PRODUCT Y", "PRODUCT-Y"]:
            target_id = "PRODUCT-Y"
        elif clean_id in ["ABC", "PRODUCT ABC", "P-ABC"]:
            target_id = "P-ABC"
        elif clean_id in ["XYZ", "PRODUCT XYZ", "P-XYZ"]:
            target_id = "P-XYZ"
        else:
            target_id = clean_id

        # Find product - exact match first
        prod = self.db.query(Product).filter(
            (Product.product_id == target_id) |
            (Product.product_id == f"PRODUCT-{target_id}") |
            (Product.product_id == f"P-{target_id}") |
            (Product.product_id == f"P{target_id}")
        ).first()

        if not prod:
            prod = self.db.query(Product).filter(
                (Product.product_id.ilike(f"%{target_id}%")) |
                (Product.name.ilike(f"%{target_id}%"))
            ).first()

        if not prod:
            return {"error": f"Product '{product_identifier}' not found in Product Master."}

        # Query all warehouses
        wh_inventory = (
            self.db.query(Inventory, Warehouse)
            .join(Warehouse, Inventory.location_id == Warehouse.warehouse_id)
            .filter(Inventory.product_id == prod.product_id, Inventory.location_type == "warehouse")
            .all()
        )

        # Query all stores
        store_inventory = (
            self.db.query(Inventory, Store)
            .join(Store, Inventory.location_id == Store.store_id)
            .filter(Inventory.product_id == prod.product_id, Inventory.location_type == "store")
            .all()
        )

        wh_data = [
            {
                "warehouse_id": w.warehouse_id,
                "warehouse_name": w.name,
                "region": w.region,
                "quantity_on_hand": inv.quantity_on_hand,
                "quantity_reserved": inv.quantity_reserved,
                "available": inv.quantity_on_hand - inv.quantity_reserved,
                "status": inv.status
            }
            for inv, w in wh_inventory
        ]

        store_data = [
            {
                "store_id": s.store_id,
                "store_name": s.name,
                "city": s.city,
                "quantity_on_hand": inv.quantity_on_hand,
                "status": inv.status
            }
            for inv, s in store_inventory
        ]

        total_wh_stock = sum(d["available"] for d in wh_data)
        total_store_stock = sum(d["quantity_on_hand"] for d in store_data)

        return {
            "product_id": prod.product_id,
            "product_name": prod.name,
            "category": prod.category,
            "total_warehouse_stock": total_wh_stock,
            "total_store_stock": total_store_stock,
            "warehouse_breakdown": wh_data,
            "store_breakdown": store_data,
            "reorder_threshold": prod.min_reorder_level
        }

    def get_delayed_purchase_orders(self, supplier_identifier: Optional[str] = None) -> List[Dict[str, Any]]:
        """Show all delayed purchase orders for a supplier (or all suppliers)."""
        query = (
            self.db.query(PurchaseOrder, Supplier)
            .join(Supplier, PurchaseOrder.supplier_id == Supplier.supplier_id)
            .filter(PurchaseOrder.status == "delayed")
        )

        if supplier_identifier:
            query = query.filter(
                (Supplier.supplier_id.ilike(f"%{supplier_identifier}%")) |
                (Supplier.name.ilike(f"%{supplier_identifier}%"))
            )

        results = query.all()
        delayed_list = []
        for po, sup in results:
            delayed_list.append({
                "po_number": po.po_number,
                "supplier_id": sup.supplier_id,
                "supplier_name": sup.name,
                "destination_warehouse": po.destination_warehouse_id,
                "order_date": po.order_date.strftime("%Y-%m-%d") if po.order_date else "",
                "expected_delivery_date": po.expected_delivery_date.strftime("%Y-%m-%d") if po.expected_delivery_date else "",
                "total_cost": po.total_cost,
                "items_count": po.items_count,
                "status": po.status,
                "notes": po.notes
            })
        return delayed_list

    def get_highest_return_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Which products have the highest return rate this month?"""
        # Calculate return counts and rate vs sales
        sql = """
        SELECT 
            p.product_id,
            p.name as product_name,
            p.category,
            COUNT(r.id) as total_returns,
            SUM(r.quantity) as return_quantity,
            SUM(r.refund_amount) as total_refunded,
            COALESCE(
                (SELECT SUM(st.quantity) FROM sales_transactions st WHERE st.product_id = p.product_id), 1
            ) as total_sold
        FROM products p
        JOIN returns r ON p.product_id = r.product_id
        GROUP BY p.product_id, p.name, p.category
        ORDER BY total_returns DESC
        LIMIT :limit
        """
        results = self.db.execute(text(sql), {"limit": limit}).fetchall()
        output = []
        for row in results:
            sold = row.total_sold or 1
            ret_qty = row.return_quantity or 0
            rate = round((ret_qty / sold) * 100.0, 2)
            output.append({
                "product_id": row.product_id,
                "product_name": row.product_name,
                "category": row.category,
                "total_returns": row.total_returns,
                "return_quantity": ret_qty,
                "total_sold": sold,
                "return_rate_pct": rate,
                "total_refunded": round(row.total_refunded, 2)
            })
        return output

    def get_vendor_for_product(self, product_identifier: str) -> Dict[str, Any]:
        """Which vendor supplies Product ABC?"""
        prod = self.db.query(Product).filter(
            (Product.product_id.ilike(f"%{product_identifier}%")) |
            (Product.name.ilike(f"%{product_identifier}%"))
        ).first()

        if not prod:
            return {"error": f"Product '{product_identifier}' not found in Product Master."}

        sup = self.db.query(Supplier).filter(Supplier.supplier_id == prod.supplier_id).first()
        return {
            "product_id": prod.product_id,
            "product_name": prod.name,
            "supplier_id": sup.supplier_id if sup else prod.supplier_id,
            "supplier_name": sup.name if sup else "Unknown Supplier",
            "contact_email": sup.email if sup else "N/A",
            "lead_time_days": sup.lead_time_days if sup else prod.lead_time_days,
            "reliability_score": sup.reliability_score if sup else 0.95,
            "status": sup.status if sup else "active"
        }

    def get_store_replenishment_needs(self, store_id: str) -> List[Dict[str, Any]]:
        """Generate replenishment requirements for a store where stock <= threshold."""
        inv_items = (
            self.db.query(Inventory, Product)
            .join(Product, Inventory.product_id == Product.product_id)
            .filter(Inventory.location_id == store_id, Inventory.location_type == "store")
            .all()
        )

        checklist = []
        for inv, prod in inv_items:
            if inv.quantity_on_hand <= inv.reorder_threshold:
                shortage = inv.reorder_threshold * 2 - inv.quantity_on_hand
                checklist.append({
                    "product_id": prod.product_id,
                    "product_name": prod.name,
                    "category": prod.category,
                    "current_stock": inv.quantity_on_hand,
                    "reorder_threshold": inv.reorder_threshold,
                    "recommended_reorder_qty": max(shortage, prod.min_reorder_level),
                    "supplier_id": prod.supplier_id,
                    "lead_time_days": prod.lead_time_days,
                    "urgency": "CRITICAL" if inv.quantity_on_hand == 0 else "HIGH"
                })
        return checklist

    def analyze_frequent_stockout_cause(self, product_id: str) -> Dict[str, Any]:
        """Analyzes why Product P100 is frequently going out of stock (demand vs replenishment vs supplier)."""
        prod = self.db.query(Product).filter(Product.product_id == product_id).first()
        if not prod:
            return {"error": f"Product {product_id} not found."}

        # Check total inventory
        invs = self.db.query(Inventory).filter(Inventory.product_id == product_id).all()
        total_stock = sum(i.quantity_on_hand for i in invs)

        # Check supplier orders
        pos = self.db.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == prod.supplier_id).all()
        delayed_pos = [po for po in pos if po.status == "delayed"]

        # Check sales velocity
        sales = self.db.query(SalesTransaction).filter(SalesTransaction.product_id == product_id).all()
        total_sold = sum(s.quantity for s in sales)

        # Check forecasts
        forecasts = self.db.query(DemandForecast).filter(DemandForecast.product_id == product_id).all()
        avg_forecast = sum(f.predicted_demand for f in forecasts) / (len(forecasts) or 1)

        return {
            "product_id": prod.product_id,
            "product_name": prod.name,
            "current_total_stock": total_stock,
            "min_reorder_level": prod.min_reorder_level,
            "supplier_id": prod.supplier_id,
            "total_sales_units": total_sold,
            "avg_predicted_demand": round(avg_forecast, 1),
            "delayed_po_count": len(delayed_pos),
            "primary_bottleneck": (
                "Supplier Delivery Delay" if len(delayed_pos) > 0 else
                "Underestimated Demand Spike" if total_sold > avg_forecast else
                "Reorder Threshold Too Low"
            )
        }

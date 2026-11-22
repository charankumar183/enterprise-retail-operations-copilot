import os
import random
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.models.retail import (
    Product, Supplier, Store, Warehouse, Inventory, Customer,
    SalesTransaction, PurchaseOrder, Promotion, Shipment,
    ProductReturn, PricingHistory, DemandForecast, Employee
)
from backend.app.models.auth import User
from backend.app.models.document import DocumentRecord, DocumentChunk
from backend.app.services.auth_service import get_password_hash
from backend.app.services.document_parser import DocumentParserService
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.hybrid_retriever import HybridRetrieverService

class SeedingService:
    @staticmethod
    def init_database():
        """Creates all relational database tables."""
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def seed_users(db: Session):
        """Seeds default users representing all required enterprise roles."""
        roles = [
            ("admin", "admin@enterprise-retail.com", "Administrator", "Chief Operations Officer"),
            ("manager", "manager105@enterprise-retail.com", "Store Manager", "Marcus Vance"),
            ("analyst", "analyst@enterprise-retail.com", "Supply Chain Analyst", "Elena Rostova"),
            ("planner", "planner@enterprise-retail.com", "Inventory Planner", "David Chen"),
            ("category", "category@enterprise-retail.com", "Category Manager", "Sarah Jenkins"),
            ("procurement", "procurement@enterprise-retail.com", "Procurement Manager", "Robert Martinez")
        ]

        for username, email, role, full_name in roles:
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                user = User(
                    username=username,
                    email=email,
                    role=role,
                    full_name=full_name,
                    hashed_password=get_password_hash("admin123"),
                    is_active=True
                )
                db.add(user)
        db.commit()

    @staticmethod
    def seed_structured_data(db: Session):
        """Seeds 14 realistic structured retail tables with cross-referenced data."""
        # Check if already seeded
        if db.query(Product).first():
            return

        print("Seeding 14 Retail Enterprise Structured Tables...")

        # 1. Suppliers
        suppliers_data = [
            Supplier(supplier_id="SUP-XYZ", name="Apex Consumer Goods Ltd", contact_name="Jonathan Vance", email="orders@apexsupply.com", phone="1-800-555-0199", category="Home & Cleaning", reliability_score=0.82, lead_time_days=10, status="active"),
            Supplier(supplier_id="SUP-ABC", name="Verdant Eco-Clean Supply", contact_name="Clara Oswald", email="supply@verdanteco.com", phone="1-800-555-0244", category="Eco Laundry", reliability_score=0.96, lead_time_days=5, status="active"),
            Supplier(supplier_id="SUP-TECH", name="Lumina Smart Devices Inc", contact_name="Arthur Pendelton", email="b2b@luminasmart.com", phone="1-800-555-0377", category="Electronics", reliability_score=0.91, lead_time_days=14, status="active"),
            Supplier(supplier_id="SUP-GROC", name="Pinnacle Farm Foods Corp", contact_name="Maria Santos", email="wholesale@pinnaclefoods.com", phone="1-800-555-0488", category="Grocery", reliability_score=0.98, lead_time_days=3, status="active"),
            Supplier(supplier_id="SUP-BEV", name="Cascade Pure Beverage Group", contact_name="Julian Drake", email="distribution@cascadepure.com", phone="1-800-555-0599", category="Beverages", reliability_score=0.94, lead_time_days=4, status="active"),
        ]
        db.add_all(suppliers_data)
        db.commit()

        # 2. Stores
        stores_data = [
            Store(store_id="STORE-105", name="Metro Supercenter Dallas", city="Dallas", state="TX", region="South", store_type="Supercenter", manager_name="Marcus Vance", daily_sales_target=32000.0),
            Store(store_id="STORE-210", name="Urban Hub Austin", city="Austin", state="TX", region="South", store_type="Express", manager_name="Rachel Green", daily_sales_target=22000.0),
            Store(store_id="STORE-301", name="Midwest Plaza Chicago", city="Chicago", state="IL", region="Midwest", store_type="Hypermarket", manager_name="Thomas Miller", daily_sales_target=45000.0),
            Store(store_id="STORE-404", name="Pacific Gateway Seattle", city="Seattle", state="WA", region="West", store_type="Supercenter", manager_name="Chloe Bennett", daily_sales_target=38000.0),
            Store(store_id="STORE-505", name="Atlantic Center New York", city="New York", state="NY", region="East", store_type="Flagship", manager_name="Harrison Ford", daily_sales_target=65000.0),
        ]
        db.add_all(stores_data)
        db.commit()

        # 3. Warehouses
        warehouses_data = [
            Warehouse(warehouse_id="WH-001", name="North Texas Distribution Hub", location="Fort Worth, TX", region="South", capacity_sqft=450000, utilization_pct=84.2, manager_name="Frank Gallagher"),
            Warehouse(warehouse_id="WH-002", name="Midwest Central Logistics Center", location="Plainfield, IN", region="Midwest", capacity_sqft=600000, utilization_pct=76.8, manager_name="Diane Lockhart"),
            Warehouse(warehouse_id="WH-CENTRAL", name="Continental Crossroads DC", location="Memphis, TN", region="South", capacity_sqft=800000, utilization_pct=91.4, manager_name="Victor Creed"),
            Warehouse(warehouse_id="WH-WEST", name="Pacific Inland Warehouse", location="Reno, NV", region="West", capacity_sqft=350000, utilization_pct=68.5, manager_name="Sandra Bullock"),
        ]
        db.add_all(warehouses_data)
        db.commit()

        # 4. Products (Specifically include P100, P-ABC, Product X, Product Y)
        products_data = [
            Product(product_id="P100", name="UltraClean Dishwasher Pods 60-Pack", category="Household Cleaning", department="Home Care", brand="Apex Clean", unit_price=18.99, cost_price=9.50, supplier_id="SUP-XYZ", min_reorder_level=120, lead_time_days=10, description="Concentrated enzyme formula dishwasher detergent pods. High sales velocity SKU with chronic stockout vulnerability."),
            Product(product_id="P-ABC", name="EcoFriendly Botanical Laundry Detergent 64oz", category="Household Cleaning", department="Home Care", brand="Verdant Eco", unit_price=14.49, cost_price=7.20, supplier_id="SUP-ABC", min_reorder_level=60, lead_time_days=5, description="Plant-based hypoallergenic laundry soap."),
            Product(product_id="P-XYZ", name="Lumina Smart Color Wi-Fi LED Bulb 4-Pack", category="Electronics", department="Hardware", brand="Lumina", unit_price=39.99, cost_price=19.00, supplier_id="SUP-TECH", min_reorder_level=40, lead_time_days=14, description="Multicolor smart ambient lighting pack."),
            Product(product_id="P-GROC1", name="Organic Artisan Sourdough Loaf 24oz", category="Bakery & Grocery", department="Fresh Grocery", brand="Pinnacle Farm", unit_price=5.99, cost_price=2.40, supplier_id="SUP-GROC", min_reorder_level=80, lead_time_days=2, description="Daily baked all-natural stone ground sourdough."),
            Product(product_id="P-BEV1", name="Sparkling Glacier Spring Water 12-Pack", category="Beverages", department="Grocery", brand="Cascade Pure", unit_price=8.99, cost_price=4.10, supplier_id="SUP-BEV", min_reorder_level=150, lead_time_days=4, description="Zero-calorie natural mountain spring mineral water."),
            Product(product_id="PRODUCT-X", name="OmniGuard Wireless Security Camera HD", category="Electronics", department="Hardware", brand="Lumina", unit_price=79.99, cost_price=42.00, supplier_id="SUP-TECH", min_reorder_level=50, lead_time_days=14, description="Weatherproof 1080p smart home security camera system."),
            Product(product_id="PRODUCT-Y", name="AromaWave Ultrasonics Essential Oil Diffuser", category="Home Goods", department="Home Care", brand="Apex Clean", unit_price=29.99, cost_price=12.50, supplier_id="SUP-XYZ", min_reorder_level=35, lead_time_days=10, description="Ceramic cool mist diffuser. Subject to customer seal leakage complaints.")
        ]
        db.add_all(products_data)
        db.commit()

        # 5. Inventory (Cross-warehouse & Store stock)
        inventories_data = [
            # P100 - stockout in stores, low in warehouses
            Inventory(product_id="P100", location_type="warehouse", location_id="WH-001", quantity_on_hand=30, quantity_reserved=25, reorder_threshold=100, safety_stock=40, status="Low Stock"),
            Inventory(product_id="P100", location_type="warehouse", location_id="WH-002", quantity_on_hand=0, quantity_reserved=0, reorder_threshold=100, safety_stock=40, status="Out of Stock"),
            Inventory(product_id="P100", location_type="warehouse", location_id="WH-CENTRAL", quantity_on_hand=85, quantity_reserved=60, reorder_threshold=150, safety_stock=60, status="Low Stock"),
            Inventory(product_id="P100", location_type="warehouse", location_id="WH-WEST", quantity_on_hand=15, quantity_reserved=15, reorder_threshold=80, safety_stock=30, status="Low Stock"),
            Inventory(product_id="P100", location_type="store", location_id="STORE-105", quantity_on_hand=4, quantity_reserved=0, reorder_threshold=45, safety_stock=20, status="Low Stock"),
            Inventory(product_id="P100", location_type="store", location_id="STORE-210", quantity_on_hand=0, quantity_reserved=0, reorder_threshold=30, safety_stock=15, status="Out of Stock"),

            # PRODUCT-X across all warehouses
            Inventory(product_id="PRODUCT-X", location_type="warehouse", location_id="WH-001", quantity_on_hand=420, quantity_reserved=40, reorder_threshold=100, safety_stock=50, status="In Stock"),
            Inventory(product_id="PRODUCT-X", location_type="warehouse", location_id="WH-002", quantity_on_hand=680, quantity_reserved=65, reorder_threshold=120, safety_stock=60, status="In Stock"),
            Inventory(product_id="PRODUCT-X", location_type="warehouse", location_id="WH-CENTRAL", quantity_on_hand=1250, quantity_reserved=110, reorder_threshold=200, safety_stock=100, status="In Stock"),
            Inventory(product_id="PRODUCT-X", location_type="warehouse", location_id="WH-WEST", quantity_on_hand=310, quantity_reserved=25, reorder_threshold=80, safety_stock=40, status="In Stock"),
            Inventory(product_id="PRODUCT-X", location_type="store", location_id="STORE-105", quantity_on_hand=28, quantity_reserved=0, reorder_threshold=15, safety_stock=8, status="In Stock"),
            Inventory(product_id="PRODUCT-X", location_type="store", location_id="STORE-210", quantity_on_hand=18, quantity_reserved=0, reorder_threshold=10, safety_stock=5, status="In Stock"),

            # P-ABC
            Inventory(product_id="P-ABC", location_type="warehouse", location_id="WH-001", quantity_on_hand=540, quantity_reserved=20, reorder_threshold=100, safety_stock=50, status="In Stock"),
            Inventory(product_id="P-ABC", location_type="store", location_id="STORE-105", quantity_on_hand=95, quantity_reserved=0, reorder_threshold=30, safety_stock=15, status="In Stock"),
            Inventory(product_id="P-ABC", location_type="store", location_id="STORE-210", quantity_on_hand=6, quantity_reserved=0, reorder_threshold=25, safety_stock=10, status="Low Stock"),

            # PRODUCT-Y
            Inventory(product_id="PRODUCT-Y", location_type="warehouse", location_id="WH-001", quantity_on_hand=180, quantity_reserved=15, reorder_threshold=50, safety_stock=25, status="In Stock"),
            Inventory(product_id="PRODUCT-Y", location_type="store", location_id="STORE-105", quantity_on_hand=14, quantity_reserved=0, reorder_threshold=15, safety_stock=5, status="Low Stock"),
            Inventory(product_id="PRODUCT-Y", location_type="store", location_id="STORE-210", quantity_on_hand=2, quantity_reserved=0, reorder_threshold=15, safety_stock=5, status="Low Stock"),
        ]
        db.add_all(inventories_data)
        db.commit()

        # 6. Customers
        customers_data = [
            Customer(customer_id="CUST-1001", name="Sarah Connor", email="sarah.connor@gmail.com", phone="555-0101", segment="Retail", loyalty_tier="Gold"),
            Customer(customer_id="CUST-1002", name="James Holden", email="jholden@roci.org", phone="555-0102", segment="Retail", loyalty_tier="Platinum"),
            Customer(customer_id="CUST-1003", name="Amos Burton", email="amos.b@baltimore.net", phone="555-0103", segment="Wholesale", loyalty_tier="Silver"),
            Customer(customer_id="CUST-1004", name="Naomi Nagata", email="nnagata@beltmail.com", phone="555-0104", segment="Retail", loyalty_tier="Bronze"),
        ]
        db.add_all(customers_data)
        db.commit()

        # 7. Sales Transactions (Generate 50 realistic sales transactions across stores)
        sales_data = []
        base_time = datetime.utcnow() - timedelta(days=7)
        for i in range(1, 60):
            st_id = f"TX-90{i:03d}"
            store = "STORE-105" if i % 2 == 0 else "STORE-210"
            prod = "P100" if i % 4 == 0 else ("PRODUCT-X" if i % 3 == 0 else "PRODUCT-Y")
            qty = (i % 3) + 1
            price = 18.99 if prod == "P100" else (79.99 if prod == "PRODUCT-X" else 29.99)
            disc = 2.0 if i % 5 == 0 else 0.0
            tot = (qty * price) - disc
            tx_time = base_time + timedelta(hours=i * 2.8)

            sales_data.append(SalesTransaction(
                transaction_id=st_id,
                store_id=store,
                customer_id=f"CUST-100{(i % 4) + 1}",
                product_id=prod,
                quantity=qty,
                unit_price=price,
                discount_amount=disc,
                total_amount=round(tot, 2),
                payment_method="Credit Card" if i % 2 == 0 else "Debit Card",
                transaction_date=tx_time
            ))
        db.add_all(sales_data)
        db.commit()

        # 8. Purchase Orders (Specifically include delayed POs for Supplier XYZ)
        po_data = [
            PurchaseOrder(po_number="PO-7701", supplier_id="SUP-XYZ", destination_warehouse_id="WH-001", order_date=datetime.utcnow() - timedelta(days=22), expected_delivery_date=datetime.utcnow() - timedelta(days=8), actual_delivery_date=None, status="delayed", total_cost=24500.0, items_count=1200, notes="Vendor reported raw chemical surfactant shortage; container delayed at rail terminal."),
            PurchaseOrder(po_number="PO-7702", supplier_id="SUP-XYZ", destination_warehouse_id="WH-CENTRAL", order_date=datetime.utcnow() - timedelta(days=19), expected_delivery_date=datetime.utcnow() - timedelta(days=5), actual_delivery_date=None, status="delayed", total_cost=31200.0, items_count=1500, notes="Carrier missed scheduled pickup slot; warehouse receiving rescheduled."),
            PurchaseOrder(po_number="PO-7703", supplier_id="SUP-XYZ", destination_warehouse_id="WH-002", order_date=datetime.utcnow() - timedelta(days=14), expected_delivery_date=datetime.utcnow() - timedelta(days=2), actual_delivery_date=None, status="delayed", total_cost=18800.0, items_count=950, notes="Customs documentation hold on packaging components."),
            PurchaseOrder(po_number="PO-7801", supplier_id="SUP-ABC", destination_warehouse_id="WH-001", order_date=datetime.utcnow() - timedelta(days=6), expected_delivery_date=datetime.utcnow() + timedelta(days=2), actual_delivery_date=None, status="shipped", total_cost=15200.0, items_count=1100, notes="On schedule via FedEx Freight."),
            PurchaseOrder(po_number="PO-7901", supplier_id="SUP-TECH", destination_warehouse_id="WH-CENTRAL", order_date=datetime.utcnow() - timedelta(days=15), expected_delivery_date=datetime.utcnow() - timedelta(days=1), actual_delivery_date=datetime.utcnow() - timedelta(days=1), status="delivered", total_cost=48000.0, items_count=600, notes="Received and cleared QA dock."),
        ]
        db.add_all(po_data)
        db.commit()

        # 9. Promotions
        promos_data = [
            Promotion(campaign_id="CAMP-2026-Q1", campaign_name="Spring Refresh Clean Home", product_category="Household Cleaning", discount_percentage=15.0, start_date=date(2026, 3, 1), end_date=date(2026, 3, 31), policy_version="Version 5", status="active", terms="Maximum 15% discount; stackable coupons disallowed per Version 5 policy."),
            Promotion(campaign_id="CAMP-2025-LEGACY", campaign_name="Winter Deep Clean Markdown", product_category="Household Cleaning", discount_percentage=25.0, start_date=date(2025, 11, 1), end_date=date(2025, 12, 31), policy_version="Version 3", status="expired", terms="Legacy 25% markdown policy with manual store manager override permitted."),
            Promotion(campaign_id="CAMP-TECH-SAVE", campaign_name="Smart Living Tech Festival", product_category="Electronics", discount_percentage=10.0, start_date=date(2026, 4, 1), end_date=date(2026, 4, 15), policy_version="Version 5", status="scheduled", terms="MAP compliance verified with Lumina Smart Devices."),
        ]
        db.add_all(promos_data)
        db.commit()

        # 10. Shipments
        shipments_data = [
            Shipment(shipment_id="SHIP-8801", po_number="PO-7701", origin_type="Supplier", origin_id="SUP-XYZ", destination_type="Warehouse", destination_id="WH-001", carrier="Old Dominion Freight", tracking_number="ODFL-993214", status="Delayed", shipped_date=datetime.utcnow() - timedelta(days=12), estimated_delivery=datetime.utcnow() - timedelta(days=8)),
            Shipment(shipment_id="SHIP-8802", po_number="PO-7702", origin_type="Supplier", origin_id="SUP-XYZ", destination_type="Warehouse", destination_id="WH-CENTRAL", carrier="Estes Express", tracking_number="EXST-441299", status="Delayed", shipped_date=datetime.utcnow() - timedelta(days=9), estimated_delivery=datetime.utcnow() - timedelta(days=5)),
            Shipment(shipment_id="SHIP-8803", po_number="PO-7801", origin_type="Supplier", origin_id="SUP-ABC", destination_type="Warehouse", destination_id="WH-001", carrier="FedEx Freight", tracking_number="FXF-771822", status="In Transit", shipped_date=datetime.utcnow() - timedelta(days=3), estimated_delivery=datetime.utcnow() + timedelta(days=2)),
        ]
        db.add_all(shipments_data)
        db.commit()

        # 11. Returns (Customer returns with reasons for return rate & complaint analytics)
        returns_data = [
            ProductReturn(return_id="RET-501", transaction_id="TX-90001", product_id="PRODUCT-Y", store_id="STORE-105", customer_id="CUST-1001", reason="Aroma diffuser reservoir leaks fluid from base gasket", quantity=1, refund_amount=29.99, return_date=datetime.utcnow() - timedelta(days=2), condition="Defective"),
            ProductReturn(return_id="RET-502", transaction_id="TX-90005", product_id="PRODUCT-Y", store_id="STORE-105", customer_id="CUST-1002", reason="Diffuser stopped misting after 2 days; plastic casing cracked", quantity=1, refund_amount=29.99, return_date=datetime.utcnow() - timedelta(days=3), condition="Defective"),
            ProductReturn(return_id="RET-503", transaction_id="TX-90011", product_id="PRODUCT-Y", store_id="STORE-210", customer_id="CUST-1003", reason="Liquid leaked during shipping and ruined packaging", quantity=2, refund_amount=59.98, return_date=datetime.utcnow() - timedelta(days=4), condition="Defective"),
            ProductReturn(return_id="RET-504", transaction_id="TX-90018", product_id="PRODUCT-Y", store_id="STORE-210", customer_id="CUST-1004", reason="Customer complaint: oil reservoir cracked on arrival", quantity=1, refund_amount=29.99, return_date=datetime.utcnow() - timedelta(days=5), condition="Defective"),
            ProductReturn(return_id="RET-505", transaction_id="TX-90008", product_id="P-XYZ", store_id="STORE-105", customer_id="CUST-1001", reason="Wi-Fi connectivity pairing error with 5GHz router", quantity=1, refund_amount=39.99, return_date=datetime.utcnow() - timedelta(days=6), condition="Restockable"),
        ]
        db.add_all(returns_data)
        db.commit()

        # 12. Pricing History
        pricing_data = [
            PricingHistory(product_id="P100", old_price=16.99, new_price=18.99, effective_date=datetime.utcnow() - timedelta(days=60), change_reason="Global surfactant chemical commodity cost increase", approved_by="Sarah Jenkins"),
            PricingHistory(product_id="PRODUCT-X", old_price=89.99, new_price=79.99, effective_date=datetime.utcnow() - timedelta(days=45), change_reason="Market price matching against competing retailers", approved_by="Sarah Jenkins"),
            PricingHistory(product_id="P-ABC", old_price=13.49, new_price=14.49, effective_date=datetime.utcnow() - timedelta(days=90), change_reason="Packaging redesign & organic certification renewal", approved_by="Sarah Jenkins"),
        ]
        db.add_all(pricing_data)
        db.commit()

        # 13. Demand Forecast
        forecast_data = [
            DemandForecast(product_id="P100", store_id="STORE-105", forecast_date=date.today(), predicted_demand=65, actual_demand=82, confidence_interval_low=55, confidence_interval_high=75, variance_pct=26.1),
            DemandForecast(product_id="P100", store_id="STORE-210", forecast_date=date.today(), predicted_demand=45, actual_demand=58, confidence_interval_low=38, confidence_interval_high=52, variance_pct=28.8),
            DemandForecast(product_id="PRODUCT-X", store_id="STORE-105", forecast_date=date.today(), predicted_demand=20, actual_demand=18, confidence_interval_low=14, confidence_interval_high=25, variance_pct=-10.0),
            DemandForecast(product_id="PRODUCT-Y", store_id="STORE-105", forecast_date=date.today(), predicted_demand=15, actual_demand=9, confidence_interval_low=10, confidence_interval_high=20, variance_pct=-40.0),
        ]
        db.add_all(forecast_data)
        db.commit()

        # 14. Employee Information
        employees_data = [
            Employee(employee_id="EMP-1051", name="Marcus Vance", role="Store Manager", store_id="STORE-105", department="Store Operations", shift="Morning", performance_rating=4.8, status="Active"),
            Employee(employee_id="EMP-1052", name="Ashley Cole", role="Assistant Manager", store_id="STORE-105", department="Store Operations", shift="Evening", performance_rating=4.5, status="Active"),
            Employee(employee_id="EMP-1053", name="Derek Jeter", role="Inventory Specialist", store_id="STORE-105", department="Logistics & Stocking", shift="Morning", performance_rating=4.6, status="Active"),
            Employee(employee_id="EMP-2101", name="Rachel Green", role="Store Manager", store_id="STORE-210", department="Store Operations", shift="Morning", performance_rating=4.7, status="Active"),
            Employee(employee_id="EMP-2102", name="Chandler Bing", role="Inventory Specialist", store_id="STORE-210", department="Stocking", shift="Night", performance_rating=4.3, status="Active"),
        ]
        db.add_all(employees_data)
        db.commit()

        print("14 Structured Tables successfully seeded!")

    @staticmethod
    def generate_unstructured_documents():
        """
        Creates realistic synthetic enterprise documents for:
        1. Store SOPs
        2. Warehouse Manuals
        3. Inventory Policies
        4. Pricing Guidelines
        5. Promotion Documents
        6. Vendor Contracts
        7. Product Catalogs
        8. Customer Service Manuals
        9. Logistics SOPs
        10. Procurement Guidelines
        11. Merchandising Documents
        12. Supply Chain Reports
        Across PDF, DOCX, TXT, CSV, Excel formats.
        """
        doc_dir = settings.DOCS_DIRECTORY
        os.makedirs(doc_dir, exist_ok=True)

        docs = {
            # 1. Warehouse Manuals (TXT / Markdown)
            "Warehouse_Receiving_Standard_Operating_Procedure.txt": """
# Standard Operating Procedure: Inbound Freight & Warehouse Receiving Protocol
**Document ID:** SOP-WH-004 | **Department:** Logistics & Warehouse Operations | **Version:** 4.2

## Section 1: Pre-Dock Arrival & Verification
Upon arrival at any enterprise distribution center (WH-001, WH-002, WH-CENTRAL, WH-WEST), the freight carrier must check in at the logistics gatehouse.
1. The driver must surrender the physical Bill of Lading (BOL), Packing Slip, and purchase order confirmation.
2. The gate clerk verifies the PO number in the Enterprise Warehouse Management System (WMS) within 15 minutes.
3. If the PO status is marked as cancelled or has invalid destination authorization, freight entry is refused.

## Section 2: Physical Seal and Damage Inspection
Before breaking the trailer security seal:
1. The receiving supervisor and carrier representative inspect the numbered high-security bolt seal.
2. Confirm the seal number matches the BOL exactly. If the seal is compromised, record photo evidence and flag container for quarantine.
3. Inspect pallet integrity for leaning stacks, crushed bottom boxes, moisture, or chemical odors.

## Section 3: Barcode Scanning and Inventory Receipt
1. Unload pallets using designated motorized pallet jacks and stage in the Inbound Receiving Lane.
2. Scan the UCC-128 barcode on each pallet into the handheld terminal.
3. Quantity discrepancies between physical piece count and advance shipping notice (ASN) exceeding 0% must be flagged in the WMS.
4. Issue a formal Goods Receipt Note (GRN) within 2 hours of trailer unloading to release merchandise into active inventory.
""",

            # 2. Inventory Policies (TXT)
            "Inventory_Replenishment_and_Stockout_Policy.txt": """
# Enterprise Inventory Policy: Replenishment Thresholds & Stockout Escalation
**Document ID:** POL-INV-2026 | **Department:** Supply Chain Planning | **Version:** 3.1

## Section 1: Store Inventory Minimum Levels and Safety Stock
All store locations (including Store 105 and Store 210) must maintain minimum safety stock equivalent to 14 days of average forward demand.
Reorder triggers:
1. When store quantity on hand reaches the reorder threshold, automated replenishment orders are generated nightly.
2. For high-velocity Fast Moving Consumer Goods (FMCG) like Product P100 (UltraClean Pods), the reorder threshold is 45 units for Supercenters and 30 units for Express formats.

## Section 2: Chronic Stockout Root Cause Analysis
A SKU is classified under Chronic Stockout Status if store shelves experience out-of-stock events > 3 times in a 30-day window.
Primary triggers include:
- Supplier delivery delays exceeding lead time tolerances.
- Demand spikes where daily sales velocity exceeds the statistical forecast by > 20%.
- Inter-warehouse transfer bottlenecks between regional distribution hubs and retail stores.

## Section 3: Emergency Escalation & Cross-Dock Transfer
In the event of an out-of-stock condition on essential SKUs:
1. The Store Manager must submit an Emergency Expedited Transfer Request to the Central Warehouse (WH-CENTRAL).
2. Central replenishment dispatch must execute within 24 hours via dedicated LTL transport.
3. The Inventory Planner must temporarily raise the safety stock multiplier to 2.5x until supplier reliability normalizes above 95%.
""",

            # 3. Promotion Documents (Version 3 vs Version 5 comparison)
            "Promotion_Governance_Policy_Version_5.txt": """
# Corporate Retail Promotion Governance Policy: Version 5
**Document ID:** POL-MKT-VER5 | **Department:** Merchandising & Marketing | **Effective:** 2026

## Section 1: Maximum Authorized Discount Thresholds
Under Version 5 guidelines:
1. Store Managers may authorize discretionary promotional markdowns up to a maximum of 15% without regional escalation.
2. Discounts between 16% and 35% require written pre-approval from the Category Director.
3. Discretionary markdowns exceeding 35% are strictly prohibited unless part of an authorized seasonal clearance drive.

## Section 2: Stackable Coupon Restrictions
Under Version 5 policy, stacking manufacturer coupons with corporate retail promotions is strictly disallowed. The point-of-sale system automatically applies only the single highest-value promotional discount at checkout.

## Section 3: Vendor Co-Op Funding Allocations
Promotions featured in weekly digital circulars require 70% Vendor Co-Op cost absorption and 30% retailer absorption. In contrast, under the previous Version 3 policy, funding was split equally at 50/50.

## Section 4: Category Exclusions
Version 5 strictly excludes Electronics, Infant Formula, Fluid Dairy, and Minimum Advertised Price (MAP) premium hardware from discretionary promotional markdowns.
""",

            "Promotion_Governance_Policy_Version_3_Legacy.txt": """
# Corporate Retail Promotion Governance Policy: Version 3 (Legacy)
**Document ID:** POL-MKT-VER3 | **Department:** Merchandising | **Status:** Superseded

## Section 1: Store Discretionary Markdowns
Under the legacy Version 3 policy, Store Managers enjoyed broad latitude to implement in-store promotional discounts of up to 25% to liquidate aging inventory or respond to local competition.

## Section 2: Multiple Coupon Acceptance
Stores permitted customer stacking of up to two manufacturer coupons alongside one in-store circular discount, provided the total discount did not exceed product wholesale cost.

## Section 3: Advertising Cost Sharing
Promotional advertising expenses were divided equally: 50% contributed by the supplier partner and 50% funded from corporate marketing reserves.
""",

            # 4. Vendor Contracts & Procurement Guidelines
            "Vendor_Master_Agreement_Supplier_XYZ.txt": """
# Master Goods and Services Procurement Agreement
**Contract ID:** VMA-SUP-XYZ-2024 | **Supplier:** Apex Consumer Goods Ltd (SUP-XYZ) | **Department:** Procurement

## Section 3: Delivery Schedules, Lead Times and Service Levels
1. Supplier SUP-XYZ agrees to deliver ordered goods to specified distribution centers (WH-001, WH-002, WH-CENTRAL) within a contracted lead time of 10 business days from PO transmission.
2. On-Time In-Full (OTIF) delivery compliance must maintain an average of 95.0% measured across rolling 90-day periods.

## Section 4: Delayed Shipment Penalties & Breach
1. In the event Supplier fails to deliver ordered goods by the agreed expected delivery date, a late delivery penalty of 1.5% of total purchase order invoice value shall accrue per business day of delay, up to a maximum of 15%.
2. For shipments delayed in excess of 7 calendar days without prior force majeure declaration, Retailer reserves the right to cancel the PO without penalty, purchase substitute merchandise from secondary vendors, and bill the net price variance back to Supplier.
""",

            # 5. Customer Service & Complaint Manuals
            "Customer_Service_Quality_Resolution_Manual.txt": """
# Customer Service Knowledge Base: Defective Merchandise & Quality Complaints
**Document ID:** CS-KB-108 | **Department:** Customer Experience & Quality Assurance

## Section 4: Handling Quality Defect Complaints for Product Y (AromaWave Diffuser)
Product Y (AromaWave Ultrasonic Essential Oil Diffuser) has exhibited elevated return rates due to ultrasonic basin seal issues.
1. Customer Complaint Protocol: When a customer reports oil leakage from the reservoir base or failure of mist dispersion, the service desk agent must immediately offer an unconditional replacement or full refund under Code QA-DEFECT.
2. Return Condition: The item must not be restocked on store shelves. The store clerk must mark the item as 'Defective / Scrapped' in the inventory return ledger.
3. Manufacturer Defect Tracking: Store customer care teams must log the serial number and batch code to assist corporate QA in escalating defect claims to Supplier SUP-XYZ.
""",

            # 6. Store SOPs (Store Operations)
            "Store_Operations_Standard_Procedures.txt": """
# Store Operations Daily Management Manual: Supercenter & Express Formats
**Document ID:** SOP-STR-012 | **Department:** Retail Operations | **Effective:** 2026

## Section 2: Morning Store Opening Routine (06:00 - 08:00)
1. Store Manager or Assistant Manager disarms perimeter alarm and completes exterior safety walkthrough.
2. Cash office supervisor prepares cash drawers with standard opening floats ($300 per standard lane, $150 per self-checkout).
3. Inventory Specialist walks primary grocery, household, and electronics aisles to perform out-of-stock scanning. Any empty shelf facing with zero on-hand stock is logged into the handheld replenishment app.
4. Receiving dock doors are opened for scheduled morning direct-store-delivery (DSD) bread, dairy, and beverage vendors.

## Section 5: Daily Operations Reporting
Store Managers are required to generate and submit the Store Daily Operations Performance Report by 22:30 nightly.
The report must capture:
- Total daily gross sales vs budgeted sales target.
- Basket size and register transaction counts.
- Zero-stock shelf scan alerts and critical replenishment requirements.
- Customer return volumes, markdown adjustments, and employee attendance rosters.
""",

            # 7. Logistics SOPs
            "Logistics_Fleet_and_Inter_Facility_Transfers.txt": """
# Standard Operating Procedure: Logistics Fleet & Inter-Facility Stock Transfers
**Document ID:** SOP-LOG-088 | **Department:** Global Supply Chain & Transportation

## Section 1: Warehouse-to-Store Delivery Windows
Dedicated fleet trailers dispatch daily from central fulfillment hubs to regional retail stores.
1. Delivery appointments must be booked in 2-hour delivery windows.
2. High-volume stores like Store 105 operate cross-dock drops twice daily (05:00 AM and 14:00 PM).
3. All pallets must be shrink-wrapped with corner protectors and verified against trailer load manifests.
""",

            # 8. Pricing Guidelines
            "Retail_Pricing_and_Markdown_Execution_Guidelines.txt": """
# Enterprise Retail Pricing Policy: Everyday Low Price (EDLP) & Markdown Schedules
**Document ID:** PRIC-GUIDE-009 | **Department:** Pricing & Revenue Management

## Section 1: Price Change Authorization
1. Price changes initiated at the corporate level take effect in store POS registers at 00:01 on the designated effective date.
2. Electronic shelf labels (ESLs) automatically synchronize with central pricing servers within 4 minutes of activation.
3. For non-ESL paper tag displays, store teams must execute physical tag replacement before doors open to customers.
""",

            # 9. Procurement Guidelines
            "Procurement_Vendor_Sourcing_and_Risk_Management.txt": """
# Strategic Sourcing & Procurement Guidelines
**Document ID:** PROC-GUIDE-101 | **Department:** Global Procurement

## Section 3: Dual Sourcing Mandate for Tier-1 Essential SKUs
To mitigate supplier delivery delays and regional stockouts, all Tier-1 consumer packaged goods categories must maintain secondary active vendors capable of meeting at least 35% of total volume requirements.
Suppliers with reliability scores below 85% are placed on probationary review.
""",

            # 10. Merchandising Documents
            "Visual_Merchandising_and_Planogram_Compliance.txt": """
# Merchandising Standards: Planogram Execution & Endcap Displays
**Document ID:** MERCH-SOP-055 | **Department:** Merchandising

## Section 2: Endcap Promotional Guidelines
Feature endcap displays must display only active promotional items authorized in the corporate promotional calendar. Feature products must maintain minimum 3-tier deep shelf backing to present full presentation to shoppers.
""",

            # 11. Product Catalogs (CSV Format)
            "Enterprise_Product_Master_Catalog.csv": """product_id,product_name,category,department,brand,unit_price,supplier_id,lead_time_days
P100,UltraClean Dishwasher Pods 60-Pack,Household Cleaning,Home Care,Apex Clean,18.99,SUP-XYZ,10
P-ABC,EcoFriendly Botanical Laundry Detergent 64oz,Household Cleaning,Home Care,Verdant Eco,14.49,SUP-ABC,5
P-XYZ,Lumina Smart Color Wi-Fi LED Bulb 4-Pack,Electronics,Hardware,Lumina,39.99,SUP-TECH,14
P-GROC1,Organic Artisan Sourdough Loaf 24oz,Bakery & Grocery,Fresh Grocery,Pinnacle Farm,5.99,SUP-GROC,2
P-BEV1,Sparkling Glacier Spring Water 12-Pack,Beverages,Grocery,Cascade Pure,8.99,SUP-BEV,4
PRODUCT-X,OmniGuard Wireless Security Camera HD,Electronics,Hardware,Lumina,79.99,SUP-TECH,14
PRODUCT-Y,AromaWave Ultrasonics Essential Oil Diffuser,Home Goods,Home Care,Apex Clean,29.99,SUP-XYZ,10
""",

            # 12. Supply Chain Reports
            "Supply_Chain_Executive_Quarterly_Report.txt": """
# Executive Supply Chain & Logistics Performance Report
**Period:** 2026 Q1 | **Prepared by:** Operations Analytics Group

## Executive Summary
Across the enterprise network of 5 flagship stores and 4 distribution hubs, overall inventory availability stood at 93.4%.
The primary operational challenges identified during this period include:
1. Vendor supplier delays from Apex Consumer Goods (SUP-XYZ), creating repeated stockouts of Product P100 across Southern retail stores.
2. Escalating customer returns in the Home Care category due to defective seals on ultrasonic diffusers (Product Y).
3. Recommended deployment of Advanced RAG Copilot to automate inventory replenishment checklists and streamline standard warehouse receiving compliance.
"""
        }

        # Write text and CSV documents to disk
        for filename, content in docs.items():
            path = os.path.join(doc_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.strip())

        # Also create a DOCX document using python-docx
        try:
            import docx
            docx_path = os.path.join(doc_dir, "Store_Opening_and_Safety_Checklist.docx")
            doc = docx.Document()
            doc.add_heading("Store Daily Opening and Physical Safety Protocol", level=1)
            doc.add_paragraph("Document ID: DOCX-STR-091 | Store Operations Division")
            doc.add_heading("Section 1: Perimeter Safety and Asset Protection", level=2)
            doc.add_paragraph("Before allowing employees or vendor delivery drivers onto the premises, the designated duty manager must inspect all external building perimeters, emergency exit push-bars, and loading dock bays.")
            doc.add_heading("Section 2: Register Terminal Startup & Float Verification", level=2)
            doc.add_paragraph("Front-end lead operators must boot up all POS registers, verify wireless payment terminal connectivity, and confirm initial float totals.")
            doc.save(docx_path)
        except Exception:
            pass

        # Also create an Excel document using openpyxl
        try:
            import openpyxl
            excel_path = os.path.join(doc_dir, "Store_Inventory_Replenishment_Matrix.xlsx")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "ReplenishmentThresholds"
            ws.append(["Product ID", "Product Name", "Store ID", "Min Safe Stock", "Reorder Threshold", "Primary DC"])
            ws.append(["P100", "UltraClean Dishwasher Pods", "STORE-105", 20, 45, "WH-001"])
            ws.append(["P100", "UltraClean Dishwasher Pods", "STORE-210", 15, 30, "WH-CENTRAL"])
            ws.append(["P-ABC", "EcoFriendly Laundry Detergent", "STORE-105", 15, 30, "WH-001"])
            ws.append(["PRODUCT-X", "OmniGuard Security Camera", "STORE-105", 8, 15, "WH-CENTRAL"])
            ws.append(["PRODUCT-Y", "AromaWave Essential Diffuser", "STORE-210", 5, 15, "WH-001"])
            wb.save(excel_path)
        except Exception:
            pass

        print(f"Created all 12 categories of realistic enterprise retail documents in {doc_dir}")

    @classmethod
    def index_all_documents(
        cls,
        db: Session,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
        hybrid_retriever: HybridRetrieverService
    ):
        """
        Parses all enterprise documents, creates parent and child chunks,
        indexes embeddings in vector store, and stores BM25 keyword index.
        """
        doc_dir = settings.DOCS_DIRECTORY
        chunker = ChunkingService()
        files = [f for f in os.listdir(doc_dir) if os.path.isfile(os.path.join(doc_dir, f))]

        all_bm25_chunks = []

        for fn in files:
            file_path = os.path.join(doc_dir, fn)
            ext = os.path.splitext(fn)[1].lower().replace(".", "")
            file_size = os.path.getsize(file_path)

            # Check if already indexed
            existing_doc = db.query(DocumentRecord).filter(DocumentRecord.filename == fn).first()
            if existing_doc:
                # Remove existing chunks before re-indexing
                db.query(DocumentChunk).filter(DocumentChunk.doc_id == existing_doc.id).delete()
                vector_store.delete_document_chunks(existing_doc.id)
                doc_record = existing_doc
            else:
                inferred_meta = DocumentParserService.infer_metadata_from_filename(fn)
                doc_record = DocumentRecord(
                    filename=fn,
                    file_type=ext,
                    doc_type=inferred_meta.get("doc_type", "Store SOPs"),
                    department=inferred_meta.get("department", "Operations"),
                    product_category=inferred_meta.get("product_category", "General"),
                    version=inferred_meta.get("version", "1.0"),
                    file_path=file_path,
                    file_size_bytes=file_size,
                    status="parsing"
                )
                db.add(doc_record)
                db.commit()
                db.refresh(doc_record)

            # Parse file
            sections = DocumentParserService.parse_file(file_path)
            meta_dict = {
                "doc_id": doc_record.id,
                "filename": doc_record.filename,
                "file_type": doc_record.file_type,
                "doc_type": doc_record.doc_type,
                "department": doc_record.department or "",
                "version": doc_record.version or "1.0",
                "product_category": doc_record.product_category or ""
            }

            # Hierarchical Parent-Child Chunking
            parent_chunks, child_chunks = chunker.create_parent_child_chunks(
                doc_id=doc_record.id,
                sections=sections,
                doc_metadata=meta_dict
            )

            # Save chunks to SQL
            for p in parent_chunks:
                db_chunk = DocumentChunk(
                    doc_id=doc_record.id,
                    chunk_id=p.chunk_id,
                    parent_chunk_id=None,
                    is_parent=True,
                    chunk_index=int(p.chunk_id.split("_")[-1]),
                    section_title=p.section_title,
                    page_number=p.page_number,
                    content=p.content,
                    metadata_json=str(p.metadata)
                )
                db.add(db_chunk)

            # Embed and index child chunks for dense retrieval
            if child_chunks:
                child_texts = [c.content for c in child_chunks]
                child_ids = [c.chunk_id for c in child_chunks]
                child_metas = [c.metadata for c in child_chunks]
                embeddings = embedding_service.embed_documents(child_texts)

                for c in child_chunks:
                    db_chunk = DocumentChunk(
                        doc_id=doc_record.id,
                        chunk_id=c.chunk_id,
                        parent_chunk_id=c.parent_chunk_id,
                        is_parent=False,
                        chunk_index=int(c.chunk_id.split("_")[-1]),
                        section_title=c.section_title,
                        page_number=c.page_number,
                        content=c.content,
                        metadata_json=str(c.metadata)
                    )
                    db.add(db_chunk)

                    # Accumulate for BM25
                    all_bm25_chunks.append({
                        "chunk_id": c.chunk_id,
                        "text": c.content,
                        "metadata": c.metadata
                    })

                # Add to Vector Store
                vector_store.add_documents(
                    ids=child_ids,
                    embeddings=embeddings,
                    metadatas=child_metas,
                    documents=child_texts
                )

            doc_record.total_chunks = len(parent_chunks) + len(child_chunks)
            doc_record.status = "indexed"
            db.commit()

        # Index all child chunks in BM25 keyword search model
        hybrid_retriever.index_for_bm25(all_bm25_chunks)
        print(f"Successfully indexed {len(all_bm25_chunks)} chunks for Vector & BM25 Hybrid Retrieval!")

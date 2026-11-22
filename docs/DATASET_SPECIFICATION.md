# Synthetic Retail Enterprise Dataset Specification

This document details the relational schema, foreign key constraints, and synthetic business data seeded for the **Enterprise AI Retail Operations & Supply Chain Assistant**.

---

## 1. Structured Relational Tables (14 Entities)

### 1. `products` (Product Master)
- **Primary Key:** `id` (Integer)
- **Unique Code:** `product_id` (VARCHAR) e.g. `P100`, `P-ABC`, `PRODUCT-X`, `PRODUCT-Y`
- **Fields:** `name`, `category`, `department`, `brand`, `unit_price`, `cost_price`, `supplier_id` (FK), `min_reorder_level`, `lead_time_days`, `description`
- **Seeded Records:** 7 core enterprise SKUs spanning Household Cleaning, Electronics, Grocery, and Home Care.

### 2. `suppliers`
- **Primary Key:** `id`, **Code:** `supplier_id` e.g. `SUP-XYZ`, `SUP-ABC`, `SUP-TECH`
- **Fields:** `name`, `contact_name`, `email`, `phone`, `category`, `reliability_score`, `lead_time_days`, `status`
- **Seeded Records:** 5 vendors with varying reliability scores (0.82 to 0.98) and contracted lead times (3 to 14 days).

### 3. `stores`
- **Primary Key:** `id`, **Code:** `store_id` e.g. `STORE-105`, `STORE-210`, `STORE-301`
- **Fields:** `name`, `city`, `state`, `region`, `store_type`, `manager_name`, `daily_sales_target`
- **Seeded Records:** 5 retail locations (Supercenter, Express, Hypermarket, Flagship).

### 4. `warehouses`
- **Primary Key:** `id`, **Code:** `warehouse_id` e.g. `WH-001`, `WH-002`, `WH-CENTRAL`, `WH-WEST`
- **Fields:** `name`, `location`, `region`, `capacity_sqft`, `utilization_pct`, `manager_name`
- **Seeded Records:** 4 major distribution hubs with realistic capacity and utilization metrics.

### 5. `inventories`
- **Primary Key:** `id`
- **Fields:** `product_id` (FK), `location_type` (`warehouse` | `store`), `location_id`, `quantity_on_hand`, `quantity_reserved`, `reorder_threshold`, `safety_stock`, `status`
- **Seeded Records:** 16 cross-facility stock records, including intentional low-stock and stockout scenarios for `P100`.

### 6. `customers`
- **Primary Key:** `id`, **Code:** `customer_id` e.g. `CUST-1001`
- **Fields:** `name`, `email`, `phone`, `segment`, `loyalty_tier`

### 7. `sales_transactions`
- **Primary Key:** `id`, **Code:** `transaction_id`
- **Fields:** `store_id` (FK), `customer_id` (FK), `product_id` (FK), `quantity`, `unit_price`, `discount_amount`, `total_amount`, `payment_method`, `transaction_date`
- **Seeded Records:** 59 realistic point-of-sale transactions across stores.

### 8. `purchase_orders`
- **Primary Key:** `id`, **Code:** `po_number` e.g. `PO-7701`, `PO-7702`, `PO-7801`
- **Fields:** `supplier_id` (FK), `destination_warehouse_id`, `order_date`, `expected_delivery_date`, `actual_delivery_date`, `status` (`pending`, `shipped`, `delivered`, `delayed`), `total_cost`, `items_count`, `notes`
- **Seeded Records:** Includes 3 delayed POs from `SUP-XYZ` demonstrating supply chain delivery bottlenecks.

### 9. `promotions`
- **Primary Key:** `id`, **Code:** `campaign_id`
- **Fields:** `campaign_name`, `product_category`, `discount_percentage`, `start_date`, `end_date`, `policy_version` (`Version 3`, `Version 5`), `status`, `terms`

### 10. `shipments`
- **Primary Key:** `id`, **Code:** `shipment_id`
- **Fields:** `po_number` (FK), `origin_type`, `origin_id`, `destination_type`, `destination_id`, `carrier`, `tracking_number`, `status`, `shipped_date`, `estimated_delivery`

### 11. `returns`
- **Primary Key:** `id`, **Code:** `return_id`
- **Fields:** `transaction_id`, `product_id` (FK), `store_id` (FK), `customer_id`, `reason`, `quantity`, `refund_amount`, `condition` (`Defective`, `Restockable`)
- **Seeded Records:** Linked customer returns for Product Y essential diffuser seal leakage.

### 12. `pricing_history`
- **Primary Key:** `id`
- **Fields:** `product_id` (FK), `old_price`, `new_price`, `effective_date`, `change_reason`, `approved_by`

### 13. `demand_forecasts`
- **Primary Key:** `id`
- **Fields:** `product_id` (FK), `store_id` (FK), `forecast_date`, `predicted_demand`, `actual_demand`, `confidence_interval_low`, `confidence_interval_high`, `variance_pct`

### 14. `employees`
- **Primary Key:** `id`, **Code:** `employee_id`
- **Fields:** `name`, `role`, `store_id` (FK), `department`, `shift`, `performance_rating`, `status`

---

## 2. Unstructured Retail Document Collection (12 Categories)

| File Name | Format | Category | Description |
| :--- | :--- | :--- | :--- |
| `Warehouse_Receiving_Standard_Operating_Procedure.txt` | TXT | Warehouse Manuals | Inbound dock check-in, BOL verification, seal checks, GRN posting. |
| `Inventory_Replenishment_and_Stockout_Policy.txt` | TXT | Inventory Policies | Safety stock rules, stockout root cause protocol, emergency transfer. |
| `Promotion_Governance_Policy_Version_5.txt` | TXT | Promotion Documents | 15% markdown limit, no stackable coupons, 70/30 vendor co-op. |
| `Promotion_Governance_Policy_Version_3_Legacy.txt` | TXT | Promotion Documents | Legacy 25% markdown limit, coupon stacking permitted, 50/50 funding. |
| `Vendor_Master_Agreement_Supplier_XYZ.txt` | TXT | Vendor Contracts | Contracted 10-day lead time, 95% OTIF, 1.5% daily delay penalty. |
| `Customer_Service_Quality_Resolution_Manual.txt` | TXT | Customer Service Manuals | Return procedure for Product Y diffuser seal defects under Code QA-DEFECT. |
| `Store_Operations_Standard_Procedures.txt` | TXT | Store SOPs | Store opening routine, cash register floats, daily operations report. |
| `Logistics_Fleet_and_Inter_Facility_Transfers.txt` | TXT | Logistics SOPs | Dedicated fleet delivery windows, cross-dock transfer schedules. |
| `Retail_Pricing_and_Markdown_Execution_Guidelines.txt` | TXT | Pricing Guidelines | Corporate price adjustments, ESL 4-minute synchronization. |
| `Procurement_Vendor_Sourcing_and_Risk_Management.txt` | TXT | Procurement Guidelines | Dual sourcing mandate for Tier-1 SKUs (minimum 35% secondary volume). |
| `Visual_Merchandising_and_Planogram_Compliance.txt` | TXT | Merchandising Documents | Endcap promotional planograms, shelf facing standards. |
| `Enterprise_Product_Master_Catalog.csv` | CSV | Product Catalogs | Tabular catalog records across departments. |
| `Store_Opening_and_Safety_Checklist.docx` | DOCX | Store SOPs | Physical perimeter inspection, cash register setup. |
| `Store_Inventory_Replenishment_Matrix.xlsx` | Excel | Inventory Policies | Tabular replenishment thresholds across stores and distribution centers. |
| `Supply_Chain_Executive_Quarterly_Report.txt` | TXT | Supply Chain Reports | Executive quarterly operational summary, stockout findings. |

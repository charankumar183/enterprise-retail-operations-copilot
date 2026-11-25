"""Recreates synthetic sample PDFs, DOCX, TXT and supporting evaluation data."""
from pathlib import Path
import json,csv,random,os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from docx import Document
from docx.shared import Inches,Pt,RGBColor

ROOT=Path(__file__).parent
OUT=ROOT/'data'/'sample_documents';OUT.mkdir(parents=True,exist_ok=True)

SOURCE={
'01_store_operations_sop':('Store Operations Standard Operating Procedure','Operations',{
'Opening and cash controls':'Store 105 and Store 210 open only after the shift lead confirms alarm disarming, staff attendance and safe cash float. The team records exceptions in the daily operations log. Shift leads validate register reconciliation at closing and report mismatches to the Store Manager before end of day.',
'Shelf availability review':'A supervisor compares shelf quantities against the inventory dashboard at opening and every four hours. Products below reorder point require a replenishment task, on-shelf scan and confirmation of backroom stock.',
'Daily handover':'Store teams provide a handover covering stock alerts, unresolved returns, customer complaints, pending deliveries and promotions. Daily reports contain quantities and confirmed issues, not estimated figures.'}),
'02_warehouse_receiving_manual':('Warehouse Receiving and Putaway Manual','Warehouse',{
'Receiving verification':'Receiving staff verify the purchase order number, supplier, shipment seal, delivery note and carton counts before recording goods receipt. Discrepancies are photographed and quarantined for supervisor review.',
'Quality inspection':'Inspect expiry dates for grocery and beverage items, check seals, compare SKU and quantity to the purchase order, and reject damaged packaging under the receiving exception procedure.',
'Putaway and audit':'Accepted units receive a location barcode; record arrival time, actual quantity and warehouse identifier. Maintain a traceable receiving log and separate rejected goods from saleable stock.'}),
'03_inventory_replenishment_policy':('Inventory Replenishment and Stockout Policy','Inventory',{
'Reorder thresholds':'For the synthetic demonstration network, store shelf stock is reviewed when available units fall below 20 and warehouse stock below 35. The SQL table inventory.reorder_point is authoritative per location and can override these default planning examples.',
'Product P100 incident':'Product P100 has a recurring shortage simulation caused by high demand and delayed replenishment purchase orders. Investigate recent sales velocity, supply lead time, warehouse holdings, pending purchase orders and store transfer possibilities before concluding a root cause.',
'Replenishment checklist':'Confirm the SKU, store code, available stock and pending purchase orders; compare seven-day demand with forecast, identify receiving delays, request warehouse transfer where eligible, and record the replenishment owner and target date.'}),
'04_pricing_guidelines':('Retail Pricing and Price Change Guidelines','Pricing',{
'Price approval':'Category Managers propose changes with reason codes. A Procurement Manager must approve vendor-cost-related adjustments; the assigned Category Manager confirms price consistency across stores before release.',
'Pricing history':'Maintain previous price, revised price, effective date, approved user and policy version. Sales dashboard revenue calculations use the unit price recorded for each transaction.',
'Exceptions':'Flag significant retail price differences between channels for review; never overwrite historical sale unit prices when catalog prices change.'}),
'05_promotion_policy_v3':('Promotion Policy — Version 3','Marketing',{
'Eligibility':'Version 3 requires Category Manager approval for new campaigns. Store team promotion notices must be issued 48 hours before the first day of a promotion.',
'Discount rules':'Version 3 limits standard discount to 15 percent. It allows manual campaign reconciliation after the promotion ends.',
'Reconciliation':'Promotion logs are reviewed once at the campaign close by a Category Manager.'}),
'06_promotion_policy_v5':('Promotion Policy — Version 5','Marketing',{
'Eligibility':'Version 5 requires both Category Manager and Procurement Manager approval for discounts above 10 percent. Store notices must be issued at least 72 hours before launch.',
'Discount rules':'Version 5 permits up to 20 percent discount when the margin guardrail is approved and stock allocation is confirmed. Unauthorized manual price overrides are prohibited.',
'Reconciliation':'Version 5 adds daily promotion reconciliation with documented exception owner, and requires store-level stock availability checks before publication.'}),
'07_vendor_agreement':('Supplier and Vendor Agreement — Synthetic','Procurement',{
'Supplier onboarding':'Procurement Managers verify supplier tax details, insurance status, item list, payment terms and regional service areas before assigning an active supplier code.',
'Late delivery rules':'Suppliers must communicate delivery delays to Procurement within one business day of discovering the incident. Open overdue purchase orders are flagged as Delayed in SQL once the expected date passes and the order remains outstanding.',
'Supplier performance':'Track on-time delivery ratio, quantity variance, damage incidents and returns attributed to supplier issues. Agreements in this sample are fictional and carry no legal effect.'}),
'08_product_catalog_guidance':('Product Catalog Data Standards','Merchandising',{
'Product master':'Each item has a unique SKU, product name, category, supplier ID and current retail price. SKU P100 is included as a synthetic stockout troubleshooting example.',
'Change management':'All attribute corrections must be reviewed, recorded and shared with stores and ecommerce channels before item data is republished.',
'Product comparison':'Product comparison uses category, retail price, supplier and source documentation rather than claiming qualities not supported by catalog records.'}),
'09_customer_service_manual':('Customer Service and Returns Manual','Customer Service',{
'Customer complaints':'Log product SKU, complaint description, customer reference, opening date and resolution owner. Do not assume that repeated complaints prove a defect without investigation.',
'Return acceptance':'Store teams inspect returned goods, verify the purchase and record the quantity, date, reason and SKU in the returns system. Refund decisions must follow the active local store returns terms.',
'Return rate analysis':'For the academic dataset, return rate is calculated as returned units divided by sold units during the requested period; results over 100 percent can occur when return and sale windows differ and must be flagged.'}),
'10_logistics_sop':('Logistics and Shipment Exception SOP','Logistics',{
'Inbound shipment tracking':'Link each shipment with the original purchase order and supplier. Monitor expected delivery date, tracking identifier and current status to detect overdue deliveries.',
'Exception escalation':'Escalate missing cartons, lost tracking identifiers and overdue purchase orders to the Supply Chain Analyst. Confirm carrier evidence before classifying a delivery root cause.',
'Warehouse transfer':'Transfers between warehouses require an originating location, destination, SKU, quantity and receiving signoff.'}),
'11_procurement_guidelines':('Procurement and Purchase Order Guidelines','Procurement',{
'Purchase order creation':'A valid PO identifies supplier, product, destination warehouse, expected receipt date and confirmed requested units. Store manager demand requests do not directly change issued purchase orders.',
'Delay management':'Investigate purchase orders with an expected delivery date in the past and status Delayed. Contact suppliers using the approved procurement escalation matrix.',
'Approval controls':'Orders exceeding a department budget threshold require Procurement Manager signoff; the threshold is maintained in the local policy configuration and is not hardcoded in this guide.'}),
'12_merchandising_guidelines':('Merchandising and Shelf Execution Guidelines','Merchandising',{
'Planogram execution':'Category Managers provide shelf layouts based on category strategy, sell-through and available capacity. Stores report any deviation in the execution tracker.',
'Availability and promotions':'Promotion shelves are checked before launch against approved stock allocations. Low-stock promoted products are escalated for substitution approval.',
'Daily merchandising review':'Review sales mix, item availability and return signals before requesting changes to shelf presentation.'}),
'13_supply_chain_report':('Supply Chain Exception and Demand Report','Supply Chain',{
'Demand signals':'The synthetic enterprise forecast table estimates planned units by product and store for the current reporting month. Forecasts must be compared against actual sales and warehouse stock.',
'P100 shortage analysis':'P100 is deliberately seeded with low stock across multiple locations. Review inventory, demand forecasts and delayed purchase orders together; documentation alone cannot verify a numerical root cause.',
'Operational actions':'Allocate receiving capacity to urgent orders, assess transfer opportunities, log stockout resolution time, and confirm actions through the daily operations report.'}),
'14_store_returns_policy':('Store Returns and Customer Refund Policy','Customer Service',{
'Return eligibility':'Returns require a valid proof of purchase and condition review. Exceptional returns require a Store Manager approval. Local legal consumer protections supersede this synthetic demonstration procedure.',
'Processing sequence':'Capture product, store, quantity, return reason, date, action owner and resolution type. Update return analytics only after the transaction is finalized.',
'Quality issues':'Escalate clusters of damaged or defective goods to procurement and warehouse quality teams with recorded evidence.'}),
'15_inventory_cycle_count':('Inventory Cycle Count and Variance Procedure','Inventory',{
'Daily counts':'Count high-risk and low-stock SKUs each morning. Record counted quantity, system quantity, variance, verifier and timestamp.',
'Variance investigation':'Investigate differences involving receiving errors, transfers, theft suspicions and return adjustments. Do not modify stock before supervisory approval.',
'Variance closure':'Attach approved documentation and update warehouse or store inventory through the controlled inventory system.'}),
'16_customer_complaints_trends':('Customer Complaints Trends — Synthetic Monthly Brief','Customer Service',{
'Complaint classification':'Group complaints by delayed delivery, damaged packaging, incorrect item and unsatisfactory quality. Use customer service records for numerical totals.',
'Product investigation':'For specific SKUs, show representative recorded complaints, compare recent returns and review the product master before escalating.',
'Reporting':'Reports must separate factual database results from recommendations and must not assert actual customer harm based on a synthetic dataset.'})
}

def add_pdf(name,title,sections):
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RTitle',parent=styles['Title'],fontSize=17,textColor=colors.HexColor('#14395e'),spaceAfter=20))
    path=OUT/(name+'.pdf')
    doc=SimpleDocTemplate(str(path),pagesize=(595,842),topMargin=60)
    story=[Paragraph(title,styles['RTitle']),Paragraph('SYNTHETIC DEMONSTRATION DATA — NOT AN OFFICIAL RETAIL POLICY',styles['Italic']),Spacer(1,18)]
    for i,(heading,content) in enumerate(sections.items(),1):
        story.append(Paragraph(f'{i}. {heading}',styles['Heading2']))
        story.append(Spacer(1,6))
        for sentence in content.split('. '):
            story.append(Paragraph(sentence.strip().rstrip('.')+'.',styles['BodyText']))
            story.append(Spacer(1,7))
        story.append(Spacer(1,12))
    def footer(c,doc):
        c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#697f96'))
        c.drawString(48,30,'SYNTHETIC ACADEMIC RETAIL DATA');c.drawRightString(550,30,f'Page {doc.page}')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)

def add_docx(name,title,sections):
    d=Document();d.add_heading(title,0)
    p=d.add_paragraph('SYNTHETIC DEMONSTRATION DATA — NOT AN OFFICIAL RETAIL POLICY');p.style='Subtitle'
    for i,(heading,content) in enumerate(sections.items(),1):
        d.add_heading(f'{i}. {heading}',level=2);d.add_paragraph(content)
    footer=d.sections[0].footer.paragraphs[0];footer.text='Synthetic academic retail data · Internal educational use only'
    d.save(str(OUT/(name+'.docx')))

metadata=[]
for i,(key,(title,department,sections)) in enumerate(SOURCE.items()):
    kind=('pdf' if i%3==0 else 'docx' if i%3==1 else 'txt')
    if kind=='pdf':add_pdf(key,title,sections)
    if kind=='docx':add_docx(key,title,sections)
    if kind=='txt':
        text=title+'\nSYNTHETIC DEMONSTRATION DATA — NOT AN OFFICIAL RETAIL POLICY\n\n'+'\n\n'.join(f'{n}. {h}\n{body}' for n,(h,body) in enumerate(sections.items(),1))
        (OUT/(key+'.txt')).write_text(text,encoding='utf-8')
    metadata.append({'filename':f'{key}.{kind}','title':title,'department':department,'region':'All','version':'3' if key.endswith('v3') else '5' if key.endswith('v5') else '1','is_synthetic':True})
(OUT/'17_supplier_contacts.csv').write_text('supplier_code,supplier_name,region,contact\nS001,Supplier 01 Logistics,South,vendor1@example.test\nS002,Supplier 02 Logistics,East,vendor2@example.test\nS003,Supplier 03 Logistics,West,vendor3@example.test\n',encoding='utf8')
metadata.append({'filename':'17_supplier_contacts.csv','title':'Synthetic Supplier Contacts','department':'Procurement','version':'1','region':'All','is_synthetic':True})
(ROOT/'data'/'metadata'/'document_manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')

pairs=[
('What is the warehouse receiving verification procedure?','02_warehouse_receiving_manual'),
('What happens to damaged cartons during receiving?','02_warehouse_receiving_manual'),
('How do staff complete warehouse putaway?','02_warehouse_receiving_manual'),
('What is the reorder threshold for a retail store?','03_inventory_replenishment_policy'),
('How should we investigate Product P100 stockouts?','03_inventory_replenishment_policy'),
('Generate a replenishment checklist for Store 210','03_inventory_replenishment_policy'),
('How do stores reconcile cash at closing?','01_store_operations_sop'),
('What is recorded in the daily store handover?','01_store_operations_sop'),
('Who approves changes to retail prices?','04_pricing_guidelines'),
('How must historical prices be recorded?','04_pricing_guidelines'),
('What discount limit was allowed by Promotion Policy Version 3?','05_promotion_policy_v3'),
('What discount limit applies in Promotion Policy Version 5?','06_promotion_policy_v5'),
('Compare Promotion Policy Version 3 and Version 5 approval rules','06_promotion_policy_v5'),
('How do suppliers notify Procurement about delivery delays?','07_vendor_agreement'),
('How are suppliers onboarded?','07_vendor_agreement'),
('Which attributes belong to a product master record?','08_product_catalog_guidance'),
('How are SKU corrections managed?','08_product_catalog_guidance'),
('What data is captured for customer complaints?','09_customer_service_manual'),
('How is the returns rate calculated?','09_customer_service_manual'),
('What triggers shipment exception escalation?','10_logistics_sop'),
('What information is needed for a warehouse transfer?','10_logistics_sop'),
('What fields are mandatory for a purchase order?','11_procurement_guidelines'),
('How should delayed purchase orders be investigated?','11_procurement_guidelines'),
('What checks are needed before putting promotion displays on shelves?','12_merchandising_guidelines'),
('How do planners use demand forecasts?','13_supply_chain_report'),
('Which actions help resolve Product P100 shortage?','13_supply_chain_report'),
('What is the proof of purchase requirement for returns?','14_store_returns_policy'),
('How are inventory cycle-count variances investigated?','15_inventory_cycle_count'),
('What categories are used to group customer complaints?','16_customer_complaints_trends'),
('How should product complaint trends be escalated?','16_customer_complaints_trends')]
questions=[]
for q,k in pairs:
    matching=next(m['filename'] for m in metadata if m['filename'].startswith(k))
    questions.append({'question':q,'expected_documents':[matching]})
(ROOT/'data'/'evaluation'/'test_questions.json').write_text(json.dumps(questions,indent=2),encoding='utf8')
print(f'Generated {len(SOURCE)} policy documents, one CSV, and {len(questions)} labeled questions')

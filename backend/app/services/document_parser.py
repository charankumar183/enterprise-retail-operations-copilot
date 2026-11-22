import os
import re
import csv
from typing import List, Dict, Any, Optional
import pypdf
import docx
import openpyxl

class ParsedSection:
    def __init__(self, title: str, content: str, page_number: int = 1, metadata: Optional[Dict[str, Any]] = None):
        self.title = title
        self.content = content.strip()
        self.page_number = page_number
        self.metadata = metadata or {}

class DocumentParserService:
    @staticmethod
    def parse_pdf(file_path: str) -> List[ParsedSection]:
        sections: List[ParsedSection] = []
        try:
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if not text.strip():
                    continue
                # Try finding headings in page
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                current_heading = lines[0] if lines else f"Page {page_idx + 1}"
                sections.append(ParsedSection(
                    title=current_heading[:100],
                    content=text,
                    page_number=page_idx + 1
                ))
        except Exception as e:
            sections.append(ParsedSection(
                title="PDF Content",
                content=f"Error reading PDF: {str(e)}",
                page_number=1
            ))
        return sections

    @staticmethod
    def parse_docx(file_path: str) -> List[ParsedSection]:
        sections: List[ParsedSection] = []
        try:
            doc = docx.Document(file_path)
            current_title = "Document Overview"
            current_paras = []
            page_counter = 1
            word_count = 0

            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                if para.style.name.startswith("Heading"):
                    if current_paras:
                        sections.append(ParsedSection(
                            title=current_title,
                            content="\n".join(current_paras),
                            page_number=page_counter
                        ))
                        current_paras = []
                    current_title = text
                else:
                    current_paras.append(text)
                    word_count += len(text.split())
                    if word_count > 300: # Approximate 300 words per page
                        page_counter += 1
                        word_count = 0

            if current_paras:
                sections.append(ParsedSection(
                    title=current_title,
                    content="\n".join(current_paras),
                    page_number=page_counter
                ))
        except Exception as e:
            sections.append(ParsedSection(
                title="DOCX Content",
                content=f"Error reading DOCX: {str(e)}",
                page_number=1
            ))
        return sections

    @staticmethod
    def parse_txt(file_path: str) -> List[ParsedSection]:
        sections: List[ParsedSection] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Split by markdown headers or double newlines
            raw_sections = re.split(r'\n(?=#{1,3}\s|[A-Z\s]{4,}:|\n\n)', content)
            page_counter = 1
            for idx, sec in enumerate(raw_sections):
                sec = sec.strip()
                if not sec:
                    continue
                first_line = sec.split("\n")[0].strip("# \t\r")
                heading = first_line[:80] if first_line else f"Section {idx + 1}"
                sections.append(ParsedSection(
                    title=heading,
                    content=sec,
                    page_number=page_counter
                ))
                if len(sec.split()) > 250:
                    page_counter += 1
        except Exception as e:
            sections.append(ParsedSection(
                title="TXT Content",
                content=f"Error reading TXT: {str(e)}",
                page_number=1
            ))
        return sections

    @staticmethod
    def parse_csv(file_path: str) -> List[ParsedSection]:
        sections: List[ParsedSection] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if not rows:
                return [ParsedSection(title="Empty CSV", content="", page_number=1)]

            header = ", ".join(rows[0])
            batch_size = 20
            page_num = 1
            for i in range(1, len(rows), batch_size):
                chunk_rows = rows[i:i+batch_size]
                text_content = f"Columns: {header}\n\nRecords:\n"
                for r in chunk_rows:
                    text_content += ", ".join(r) + "\n"
                sections.append(ParsedSection(
                    title=f"CSV Records {i} to {min(i+batch_size-1, len(rows)-1)}",
                    content=text_content,
                    page_number=page_num
                ))
                page_num += 1
        except Exception as e:
            sections.append(ParsedSection(
                title="CSV Content",
                content=f"Error reading CSV: {str(e)}",
                page_number=1
            ))
        return sections

    @staticmethod
    def parse_excel(file_path: str) -> List[ParsedSection]:
        sections: List[ParsedSection] = []
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            page_num = 1
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                rows = list(sheet.iter_rows(values_only=True))
                if not rows:
                    continue
                header = [str(c) if c is not None else "" for c in rows[0]]
                header_str = " | ".join(header)
                body_lines = []
                for row in rows[1:100]: # top 100 rows per sheet
                    row_str = " | ".join([str(c) if c is not None else "" for c in row])
                    if any(row_str.strip()):
                        body_lines.append(row_str)
                content = f"Sheet: {sheet_name}\nColumns: {header_str}\n\nData:\n" + "\n".join(body_lines)
                sections.append(ParsedSection(
                    title=f"Sheet: {sheet_name}",
                    content=content,
                    page_number=page_num
                ))
                page_num += 1
        except Exception as e:
            sections.append(ParsedSection(
                title="Excel Content",
                content=f"Error reading Excel: {str(e)}",
                page_number=1
            ))
        return sections

    @classmethod
    def parse_file(cls, file_path: str) -> List[ParsedSection]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return cls.parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return cls.parse_docx(file_path)
        elif ext in [".csv"]:
            return cls.parse_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            return cls.parse_excel(file_path)
        else:
            return cls.parse_txt(file_path)

    @staticmethod
    def infer_metadata_from_filename(filename: str) -> Dict[str, str]:
        fn_lower = filename.lower()
        meta = {
            "doc_type": "Store SOPs",
            "department": "Operations",
            "product_category": "General",
            "region": "National",
            "version": "1.0",
            "store": "",
            "warehouse": "",
            "supplier": "",
            "promotion_campaign": ""
        }
        if "warehouse" in fn_lower or "receiving" in fn_lower:
            meta["doc_type"] = "Warehouse Manuals"
            meta["department"] = "Logistics"
        elif "inventory" in fn_lower or "replenish" in fn_lower or "stock" in fn_lower:
            meta["doc_type"] = "Inventory Policies"
            meta["department"] = "Supply Chain"
        elif "pricing" in fn_lower or "markdown" in fn_lower:
            meta["doc_type"] = "Pricing Guidelines"
            meta["department"] = "Merchandising"
        elif "promotion" in fn_lower or "promo" in fn_lower:
            meta["doc_type"] = "Promotion Documents"
            meta["department"] = "Marketing"
        elif "vendor" in fn_lower or "contract" in fn_lower or "supplier" in fn_lower:
            meta["doc_type"] = "Vendor Contracts"
            meta["department"] = "Procurement"
        elif "catalog" in fn_lower or "product" in fn_lower:
            meta["doc_type"] = "Product Catalogs"
            meta["department"] = "Merchandising"
        elif "customer" in fn_lower or "complaint" in fn_lower or "service" in fn_lower:
            meta["doc_type"] = "Customer Service Manuals"
            meta["department"] = "Customer Care"
        elif "logistics" in fn_lower or "shipping" in fn_lower:
            meta["doc_type"] = "Logistics SOPs"
            meta["department"] = "Logistics"
        elif "procurement" in fn_lower or "purchasing" in fn_lower:
            meta["doc_type"] = "Procurement Guidelines"
            meta["department"] = "Procurement"
        elif "report" in fn_lower:
            meta["doc_type"] = "Supply Chain Reports"
            meta["department"] = "Analytics"

        # Version regex
        v_match = re.search(r'version[_\s-]*(\d+(\.\d+)?)', fn_lower)
        if v_match:
            meta["version"] = f"Version {v_match.group(1)}"
        elif "v3" in fn_lower:
            meta["version"] = "Version 3"
        elif "v5" in fn_lower:
            meta["version"] = "Version 5"

        return meta

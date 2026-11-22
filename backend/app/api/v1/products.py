from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.retail import Product
from backend.app.schemas.retail import ProductOut

router = APIRouter(prefix="/products", tags=["Product Catalog"])

@router.get("", response_model=List[ProductOut])
def get_products(
    search: Optional[str] = Query(None, description="Search by product name, ID, or brand"),
    category: Optional[str] = Query(None, description="Filter by category"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    """Product Search across enterprise product catalog with category and text filters."""
    query = db.query(Product)
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.product_id.ilike(f"%{search}%")) |
            (Product.brand.ilike(f"%{search}%"))
        )
    if category:
        query = query.filter(Product.category == category)
    if department:
        query = query.filter(Product.department == department)
        
    return query.all()

@router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    """Retrieve full product master details by product ID."""
    prod = db.query(Product).filter(Product.product_id == product_id.upper()).first()
    if not prod:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

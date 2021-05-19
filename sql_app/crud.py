from sqlalchemy.orm import Session
from sqlalchemy import insert

from sql_app import models


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )


def get_suppliers(db: Session):
    return db.query(models.Supplier.SupplierID, models.Supplier.CompanyName).order_by(models.Supplier.SupplierID).all()


def get_supplier(db: Session, supplier_id: int):
    return (
        db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first()
    )


def get_suppliers_products(db: Session, supplier_id: int):
    products = db.query(
        models.Product.ProductID,
        models.Product.ProductName,
        models.Product.Discontinued,
        models.Category
    ).join(models.Category, models.Supplier
           ).filter(models.Supplier.SupplierID == supplier_id). \
        order_by(models.Product.ProductID.desc())
    return products.all()


def post_suppliers(supplier, db: Session):
    db_insert = (
        insert(models.Supplier).values(**supplier.dict(exclude_none=True)).returning(models.Supplier)
    )
    result = db.execute(db_insert)
    db.commit()
    return next(result)

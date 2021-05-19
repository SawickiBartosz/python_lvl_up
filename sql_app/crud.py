import random

from sqlalchemy.orm import Session
from sqlalchemy import insert, update, delete

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
    vals = supplier.dict(exclude_none=True)
    vals['SupplierID'] = random.randint(1000, 2000)
    print(vals)
    db_insert = (
        insert(models.Supplier).values(**vals).returning(models.Supplier)
    )
    result = db.execute(db_insert)
    db.commit()
    return next(result)


def put_supplier(supplier_id: int, supplier, db: Session):
    vals = supplier.dict(exclude_none=True)
    db_update = (
        update(models.Supplier).
            where(models.Supplier.SupplierID == supplier_id).
            values(**vals).returning(models.Supplier)
    )
    result = db.execute(db_update)
    db.commit()
    return next(result)


def del_supplier(supplier_id: int, db: Session):
    db_del = (
        delete(models.Supplier).
            where(models.Supplier.SupplierID == supplier_id).returning(models.Supplier.SupplierID)
    )
    result = db.execute(db_del)
    db.commit()

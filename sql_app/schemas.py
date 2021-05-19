from typing import Optional

from pydantic import BaseModel, PositiveInt, constr


class Shipper(BaseModel):
    ShipperID: PositiveInt
    CompanyName: constr(max_length=40)
    Phone: constr(max_length=24)

    class Config:
        orm_mode = True


class SupplierIdName(BaseModel):
    SupplierID: PositiveInt
    CompanyName: constr(max_length=40)

    class Config:
        orm_mode = True


class SupplierAll(SupplierIdName):
    ContactName: Optional[constr(max_length=30)] = None
    ContactTitle: Optional[constr(max_length=30)] = None
    Address: Optional[constr(max_length=60)] = None
    City: Optional[constr(max_length=15)] = None
    Region: Optional[constr(max_length=15)] = None
    PostalCode: Optional[constr(max_length=10)] = None
    Country: Optional[constr(max_length=15)] = None
    Phone: Optional[constr(max_length=24)] = None
    Fax: Optional[constr(max_length=24)] = None
    HomePage: Optional[str] = None

    class Config:
        orm_mode = True


class SupplierShort(BaseModel):
    SupplierID = PositiveInt
    CompanyName = constr(max_length=40)

    class Config:
        orm_mode = True


class CategoryNameID(BaseModel):
    CategoryID: PositiveInt
    CategoryName: constr(max_length=40)

    class Config:
        orm_mode = True


class Product(BaseModel):
    ProductID: PositiveInt
    ProductName: constr(max_length=40)
    Category: Optional[CategoryNameID]
    Discontinued: int

    class Config:
        orm_mode = True


class SupplierPost(BaseModel):
    CompanyName: constr(max_length=40)
    ContactName: Optional[constr(max_length=30)] = None
    ContactTitle: Optional[constr(max_length=30)] = None
    Address: Optional[constr(max_length=60)] = None
    City: Optional[constr(max_length=15)] = None
    PostalCode: Optional[constr(max_length=10)] = None
    Country: Optional[constr(max_length=15)] = None
    Phone: Optional[constr(max_length=24)] = None

    class Config:
        orm_mode = True


class SupplierToAdd(SupplierPost):
    pass


class SupplierAdded(SupplierPost):
    SupplierID: PositiveInt
    Fax: Optional[constr(max_length=24)] = None
    HomePage: Optional[str] = None


class SupplierToUpdate(SupplierPost):
    CompanyName: Optional[constr(max_length=40)]

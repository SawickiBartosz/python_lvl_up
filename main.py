import base64
import binascii
import datetime as dt
import hashlib
import os
import random
import secrets
import sqlite3
import psycopg2
import uuid
from contextlib import contextmanager
from datetime import datetime
from hashlib import sha512
from typing import Optional, List
from urllib.parse import urlparse
from sqlalchemy.orm import Session

import crud
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, PositiveInt
from starlette.authentication import AuthenticationError

import schemas
from database import get_db
from views import router as northwind_api_router

result = urlparse(os.getenv("SQLALCHEMY_DATABASE_URL"))

username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port
ps_conn = psycopg2.connect(
    database=database,
    user=username,
    password=password,
    host=hostname,
    port=port
)
cursor = ps_conn.cursor()


class HelloResp(BaseModel):
    msg: str


class Person(BaseModel):
    name: str
    surname: str


class New_category(BaseModel):
    name: str


app = FastAPI()
app.counter = 0
app.id_counter = 0
app.people = {}
app.token_value = ''
app.session_token = ''

app.include_router(northwind_api_router, tags=["northwind"])

security = HTTPBasic()


@app.get('/counter')
def counter():
    app.counter += 1
    return app.counter


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hello/{name}")
def hello_name_view(name: str):
    return f"Hello {name}"


@app.get("/hello/{name}", response_model=HelloResp)
def hello_name_view(name: str):
    return HelloResp(msg=f"Hello {name}")


@app.get('/method')
def which_method_get():
    return {"method": "GET"}


@app.post('/method', status_code=201)
def which_method_post():
    return {"method": "POST"}


@app.delete('/method', status_code=200)
def which_method_delete():
    return {"method": "DELETE"}


@app.put('/method', status_code=200)
def which_method_put():
    return {"method": "PUT"}


@app.options('/method', status_code=200)
def which_method_options():
    return {"method": "OPTIONS"}


@app.get('/auth')
def check_password(response: Response, password=None, password_hash=None):
    if password is None or password_hash is None or password == '' or password_hash == '':
        response.status_code = 401
        return
    if hashlib.sha512(password.encode()).hexdigest() == password_hash:
        response.status_code = 204
    else:
        response.status_code = 401


@app.post('/register')
def vac_register(response: Response, person: Person):
    def count_letters_in_str(string):
        num = 0
        for char in string:
            if char.isalpha():
                num += 1
        return num

    app.id_counter += 1
    curr_id = app.id_counter
    today_date = dt.date.today()
    days = count_letters_in_str(person.name) + count_letters_in_str(person.surname)
    vaccination_date = (
            today_date + dt.timedelta(days=days))

    result = {
        "id": curr_id,
        "name": person.name,
        "surname": person.surname,
        "register_date": today_date.isoformat(),
        "vaccination_date": vaccination_date.isoformat()
    }
    if result in app.people.values():
        response.status_code = 409
        return
    response.status_code = 201
    app.people.update({curr_id: result})
    return result


@app.get('/patient/{id}')
def get_patient(id: int, response: Response):
    if id < 1:
        response.status_code = 400
        return

    if id not in app.people.keys():
        response.status_code = 404
        return

    return app.people.get(id)


@app.get('/hello', response_class=HTMLResponse)
def hello_html():
    return "<h1>Hello! Today date is " + dt.datetime.today().strftime('%Y-%m-%d') + "</h1>"


@app.post('/login_session')
def login_session(response: Response, request: Request):
    auth = request.headers["Authorization"]
    try:
        scheme, credentials = auth.split()
        if scheme.lower() != 'basic':
            return
        decoded = base64.b64decode(credentials).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise AuthenticationError('Invalid basic auth credentials')
    username, _, password = decoded.partition(":")
    if username == '4dm1n' and password == 'NotSoSecurePa$$':
        session_token = str(random.uniform(0, 1))
        app.session_token = session_token
        response.set_cookie(key="session_token", value=session_token)
        response.status_code = 201
    else:
        raise HTTPException(status_code=401, detail="Unathorised")


@app.post('/login_token')
def login_token(response: Response, request: Request):
    auth = request.headers["Authorization"]
    try:
        scheme, credentials = auth.split()
        if scheme.lower() != 'basic':
            return
        decoded = base64.b64decode(credentials).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise AuthenticationError('Invalid basic auth credentials')
    username, _, password = decoded.partition(":")
    if username == '4dm1n' and password == 'NotSoSecurePa$$':
        token_value = str(random.uniform(0, 1))
        app.token_value = token_value
        response.status_code = 201
        return {"token": token_value}
    else:
        raise HTTPException(status_code=401, detail="Unathorised")


@app.get('/welcome_session')
def welcome_session(format: str, session_token: Optional[str] = Cookie(None)):
    if session_token != app.session_token:
        raise HTTPException(status_code=401, detail="Unathorised")
    if format == 'json':
        return Response(content={'message': 'Welcome!'}, media_type='application/json')
    elif format == 'html':
        return Response(content='<h1>Welcome!</h1>', media_type='text/html')
    else:
        return Response(content='Welcome!', media_type='plain/text')


@app.get('/welcome_token')
def welcome_token(token: str, format: str):
    if token != app.token_value:
        raise HTTPException(status_code=401, detail="Unathorised")
    if format == 'json':
        return Response(content={'message': 'Welcome!'},
                        media_type='application/json',
                        status_code=200)
    elif format == 'html':
        return Response(content='<h1>Welcome!</h1>', media_type='text/html',
                        status_code=200)
    else:
        return Response(content='Welcome!', media_type='plain/text',
                        status_code=200)


app = FastAPI()
app.secret_key = "T00Sh0rtAppS3cretK3y"
app.username = "4dm1n"
app.password = "NotSoSecurePa$$"
app.api_token: Optional[str] = None
app.session_token: Optional[str] = None


def add_token(token: str, cache_ns: str):
    setattr(app, cache_ns, token)


def remove_token(cache_ns: str):
    setattr(app, cache_ns, None)


def generate_token(request: Request):
    return sha512(
        bytes(
            f"{uuid.uuid4().hex}{app.secret_key}{request.headers['authorization']}",
            "utf-8",
        )
    ).hexdigest()


def auth_basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    correct_user = secrets.compare_digest(credentials.username, app.username)
    correct_pass = secrets.compare_digest(credentials.password, app.password)
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
        )

    return True


def auth_session(session_token: str = Cookie(None)):
    if app.session_token and session_token == app.session_token:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
    )


def auth_token(token: Optional[str] = None):
    if app.api_token and token == app.api_token:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
    )


@contextmanager
def response_class(format: str):
    resp_cls = PlainTextResponse
    if format == "json":
        resp_cls = JSONResponse
    if format == "html":
        resp_cls = HTMLResponse

    yield resp_cls


@contextmanager
def response_welcome_msg(format: str):
    resp_msg = "Welcome!"
    if format == "json":
        resp_msg = {"message": "Welcome!"}
    if format == "html":
        resp_msg = "<h1>Welcome!</h1>"

    yield resp_msg


@app.get("/hello", response_class=HTMLResponse)
def read_root_hello():
    return f"""
    <html>
        <head>
            <title></title>
        </head>
        <body>
            <h1>Hello! Today date is {datetime.now().date()}</h1>
        </body>
    </html>
    """


@app.post("/login_session", status_code=201, response_class=HTMLResponse)
def create_session(
        request: Request, response: Response, auth: bool = Depends(auth_basic_auth)
):
    token = generate_token(request)
    add_token(token, "session_token")
    response.set_cookie(key="session_token", value=token)
    return ""


@app.post("/login_token", status_code=201)
def create_token(request: Request, auth: bool = Depends(auth_basic_auth)):
    token = generate_token(request)
    add_token(token, "api_token")
    return {"token": token}


@app.get("/welcome_session")
def show_welcome_session(auth: bool = Depends(auth_session), format: str = ""):
    with response_class(format) as resp_cls:
        with response_welcome_msg(format) as resp_msg:
            return resp_cls(content=resp_msg)


@app.get("/welcome_token")
def show_welcome_token(auth: bool = Depends(auth_token), format: str = ""):
    with response_class(format) as resp_cls:
        with response_welcome_msg(format) as resp_msg:
            return resp_cls(content=resp_msg)


@app.get("/logged_out")
def logged_out(format: str = ""):
    with response_class(format) as resp_cls:
        if format == "json":
            return resp_cls(content={"message": "Logged out!"})
        if format == "html":
            return resp_cls(content="<h1>Logged out!</h1>")

        return resp_cls(content="Logged out!")


@app.delete("/logout_session")
def logout_session(auth: bool = Depends(auth_session), format: str = ""):
    remove_token("session_token")
    return RedirectResponse(
        url=f"/logged_out?format={format}", status_code=status.HTTP_302_FOUND
    )


@app.delete("/logout_token")
def logout_token(auth: bool = Depends(auth_token), format: str = ""):
    remove_token("api_token")
    return RedirectResponse(
        url=f"/logged_out?format={format}", status_code=status.HTTP_302_FOUND
    )


@app.get('/categories', status_code=200)
def get_categories():
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        categories = cursor.execute("SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID").fetchall()
        parsed = [{"id": cat[0], "name": cat[1]} for cat in categories]
        return {
            "categories": parsed
        }


@app.get("/customers", status_code=200)
def get_customers():
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        customers = cursor.execute("""
            SELECT CustomerID, CompanyName, 
            (COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '') || ' ' || 
            COALESCE(City, '') || ' ' || COALESCE(Country, '')) 
            FROM Customers ORDER BY UPPER(CustomerID)""").fetchall()
        parsed = [{"id": customer[0],
                   "name": customer[1],
                   "full_address": customer[2]} for customer in customers]
        return {
            "customers": parsed
        }


@app.get("/products/{id}")
def get_product(id: int):
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        product = cursor.execute("""
               SELECT ProductID, ProductName
               FROM Products WHERE ProductID=?""", (str(id),)).fetchone()
        if product is None:
            raise HTTPException(status_code=404)
        parsed = {"id": product[0],
                  "name": product[1]}
        return parsed


@app.get("/employees", status_code=200)
def get_employees(limit: int = 20, offset: int = 0, order: str = "EmployeeID"):
    if order not in ('first_name', 'last_name', 'city', 'EmployeeID'):
        raise HTTPException(status_code=400)
    if order == 'first_name':
        order = "FirstName"
    elif order == 'last_name':
        order = "LastName"
    elif order == "city":
        order = "City"
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        employees = cursor.execute("""
               SELECT EmployeeID, LastName, FirstName, City 
               FROM Employees ORDER BY """ + order +
                                   " LIMIT " + str(limit) + " OFFSET " + str(offset)).fetchall()
        parsed = [{"id": e[0],
                   "last_name": e[1],
                   "first_name": e[2],
                   "city": e[3]} for e in employees]
        return {"employees": parsed}


@app.get("/products_extended")
def get_product_extended():
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        products = cursor.execute("""
               SELECT p.ProductID, p.ProductName, c.CategoryName, s.CompanyName FROM Products p  
               JOIN Categories c on c.CategoryID=p.CategoryID
               JOIN Suppliers s on s.SupplierID=p.SupplierID
               ORDER BY ProductID""").fetchall()

        parsed = [{"id": product[0],
                   "name": product[1],
                   "category": product[2],
                   "supplier": product[3]} for product in products]
        return {"products_extended": parsed}


@app.get("/products/{id}/orders", status_code=200)
def get_orders_of_product(id: int):
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        product = cursor.execute("SELECT ProductName FROM Products WHERE ProductID = ?", (str(id),)).fetchone()
        if product is None:
            raise HTTPException(status_code=404)
        orders = cursor.execute("""
            SELECT o.OrderID, c.CompanyName, od.Quantity, round((1-od.Discount)*od.UnitPrice*od.Quantity,2)
            FROM Orders o  
            JOIN [Order Details] od on od.OrderID=o.OrderID
            JOIN Customers c on c.CustomerID=o.CustomerID
            WHERE od.ProductID = ?""", (str(id),)).fetchall()

        parsed = [{
            "id": order[0],
            "customer": order[1],
            "quantity": order[2],
            "total_price": order[3],
        } for order in orders]
        return {"orders": parsed}


@app.post('/categories', status_code=201)
def post_category(new_cat: New_category):
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Categories (CategoryName) VALUES (?)", (new_cat.name,))
        connection.commit()
        result = cursor.execute("SELECT CategoryID, CategoryName FROM Categories WHERE CategoryName=?",
                                (new_cat.name,)).fetchone()
        return {"id": result[0],
                "name": result[1]}


@app.put("/categories/{id}", status_code=200)
def update_category(id: int, new_cat: New_category):
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        cursor.execute("UPDATE Categories SET CategoryName = ? WHERE CategoryID=?", (new_cat.name, id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404)
        connection.commit()
        result = cursor.execute("SELECT CategoryID, CategoryName FROM Categories WHERE CategoryID=?",
                                (id,)).fetchone()
        return {"id": result[0],
                "name": result[1]}


@app.delete("/categories/{id}", status_code=200)
def delete_category(id: int):
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Categories WHERE CategoryID=?", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404)
        connection.commit()
        return {"deleted": 1}


@app.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
async def get_supplier(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = cursor.execute('SELECT * FROM Suppliers WHERE SupplierId=?', (supplier_id,)).fetchone()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    parsed = {
        "SupplierID": db_supplier[0],
        "CompanyName": db_supplier[1],
        "ContactName": db_supplier[2],
        "ContactTitle": db_supplier[3],
        "Address": db_supplier[4],
        "City": db_supplier[5],
        "Region": db_supplier[6],
        "PostalCode": db_supplier[7],
        "Country": db_supplier[8],
        "Phone": db_supplier[9],
        "Fax":db_supplier[10],
        "HomePage": db_supplier[11],
    }
    return parsed


@app.get("/suppliers", response_model=List[schemas.SupplierShort])
async def get_suppliers(db: Session = Depends(get_db)):
    return crud.get_suppliers(db)

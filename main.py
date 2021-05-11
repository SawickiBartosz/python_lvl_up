import base64
import binascii
import datetime as dt
import hashlib
import random
import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from hashlib import sha512
from typing import Optional

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.authentication import AuthenticationError


class HelloResp(BaseModel):
    msg: str


class Person(BaseModel):
    name: str
    surname: str


app = FastAPI()
app.counter = 0
app.id_counter = 0
app.people = {}
app.token_value = ''
app.session_token = ''

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
            FROM Customers ORDER BY (CustomerID)""").fetchall()
        for i, customer in enumerate(customers):
            customer_list = list(customer)
            for j, column in enumerate(customer):
                if column is None:
                    customer_list[j] = ' '
            customers[i] = tuple(customer_list)

        parsed = [{"id": customer[0],
                   "name": customer[1],
                   "full_address": ' '.join(customer[2:5])} for customer in customers]
        return {
            "customers": parsed
        }

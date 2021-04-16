import datetime as dt
import hashlib
from fastapi import FastAPI, Response, status
from pydantic import BaseModel


class HelloResp(BaseModel):
    msg: str


class Person(BaseModel):
    name: str
    surname: str


app = FastAPI()
app.counter = 0
app.id_counter = 0
app.people = []


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
    if password is None or password_hash is None:
        response.status_code = 401
        return
    if hashlib.sha512(password.encode()).hexdigest() == password_hash:
        response.status_code = 204
    else:
        response.status_code = 401


@app.post('/register', status_code=201)
def vac_register(person: Person):
    app.id_counter += 1
    today_date = dt.date.today()
    vaccination_date = (
            today_date + dt.timedelta(days=len(person.name.strip()) + len(person.surname.strip()))).isoformat()

    result = {
        "id": app.id_counter,
        "name": person.name,
        "surname": person.surname,
        "register_date": today_date.isoformat(),
        "vaccination_date": vaccination_date
    }
    app.people.append(result)
    return result

import datetime as dt
import hashlib
from fastapi import FastAPI, Response
from pydantic import BaseModel


class HelloResp(BaseModel):
    msg: str


class Person(BaseModel):
    name: str
    surname: str


app = FastAPI()
app.counter = 0
app.id_counter = 0
app.people = {}


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
    today_date = dt.date.today()
    days = count_letters_in_str(person.name) + count_letters_in_str(person.surname)
    vaccination_date = (
            today_date + dt.timedelta(days=days))

    result = {
        "id": app.id_counter,
        "name": person.name,
        "surname": person.surname,
        "register_date": today_date.isoformat(),
        "vaccination_date": vaccination_date.isoformat()
    }
    if result in app.people.values():
        response.status_code = 409
        return
    response.status_code = 201
    app.people.update({app.id_counter: result})
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

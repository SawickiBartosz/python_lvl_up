from fastapi import FastAPI
from pydantic import BaseModel


class HelloResp(BaseModel):
    msg: str


app = FastAPI()
app.counter = 0


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


@app.delete('/method')
def which_method_delete():
    return {"method": "DELETE"}


@app.put('/method')
def which_method_put():
    return {"method": "PUT"}


@app.options('/method')
def which_method_options():
    return {"method": "OPTIONS"}

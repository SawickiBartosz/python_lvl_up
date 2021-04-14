import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world!"}


def test_hello_name():
    name = 'Kamila'
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.text == f'"Hello {name}"'


@pytest.mark.parametrize("name", ["Zenek", "Marek", "Alojzy Niezdąży"])
def test_hello_name(name: str):
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.text == f'"Hello {name}"'


def test_counter():
    response = client.get(f"/counter")
    assert response.status_code == 200
    assert response.text == "1"
    # 2nd Try
    response = client.get(f"/counter")
    assert response.status_code == 200
    assert response.text == "2"


def test_which_method_get():
    response = client.get(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "GET"}


def test_which_method_post():
    response = client.post(f"/method")
    assert response.status_code == 201
    assert response.json() == {"method": "POST"}


def test_which_method_options():
    response = client.options(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "OPTIONS"}

import datetime as dt
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


def test_check_password_correct():
    response = client.get(
        f'/auth?password=haslo&password_hash=013c6889f799cd986a735118e1888727d1435f7f623d05d58c61bf2cd8b49ac90105e5786ceaabd62bbc27336153d0d316b2d13b36804080c44aa6198c533215')
    assert response.status_code == 204


def test_check_password_incorrect():
    response = client.get(
        f'/auth?password=haslo&password_hash=f34ad4b3ae1e2cf33092e2abb60dc0444781c15d0e2e9ecdb37e4b14176a0164027b05900e09fa0f61a1882e0b89fbfa5dcfcc9765dd2ca4377e2c794837e091')
    assert response.status_code == 401


def test_check_password_empty():
    response = client.get(f'/auth?password=&password_hash=')
    assert response.status_code == 401


def test_check_password_empty2():
    response = client.get(f'/auth')
    assert response.status_code == 401


def test_vac_register():
    body = {
        "name": "Jan",
        "surname": "Kowalski"
    }
    response = client.post('/register', json=body)
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Jan",
        "surname": "Kowalski",
        "register_date": dt.date.today().isoformat(),
        "vaccination_date": (dt.date.today() + dt.timedelta(days=11)).isoformat()
    }


def test_vac_register_digits():
    body = {
        "name": "Jan1",
        "surname": "Kowalski"
    }
    response = client.post('/register', json=body)
    assert response.status_code == 201
    assert response.json() == {
        "id": 2,
        "name": "Jan1",
        "surname": "Kowalski",
        "register_date": dt.date.today().isoformat(),
        "vaccination_date": (dt.date.today() + dt.timedelta(days=11)).isoformat()
    }

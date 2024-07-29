import pytest
import requests
from http import HTTPStatus
from app.models.user import User, UserUpdate


def get_user_id_by_email(app_url: str, email: str):
    users = requests.get(f"{app_url}/api/users/").json()['items']
    for user in users:
        if user['email'] == email:
            return user['id']
    raise 'User did not find'


@pytest.fixture()
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()['items']


@pytest.fixture()
def user_id_too_much(fill_test_data):
    return len(fill_test_data) + 1


@pytest.fixture
def data_create_user(app_url) -> dict:
    create_user = {
        "email": "create_test@reqres.in",
        "first_name": "Rachel",
        "last_name": "Howell",
        "avatar": "https://reqres.in/img/faces/13-image.jpg"
    }
    yield create_user
    delete_response = requests.delete(
        f'{app_url}/api/users/{get_user_id_by_email(app_url, create_user["email"])}')
    assert delete_response.status_code == HTTPStatus.OK


@pytest.fixture
def data_created_user(app_url) -> dict:
    created_user = {
        "email": "created_super_user@reqres.in",
        "first_name": "Maxim",
        "last_name": "Smith",
        "avatar": "https://reqres.in/img/faces/10-image.jpg"
    }
    response_created = requests.post(f"{app_url}/api/users", json=created_user)
    assert response_created.status_code == HTTPStatus.CREATED
    created_user = response_created.json()
    return created_user


@pytest.fixture
def delete_created_user(app_url, data_created_user):
    yield
    delete_response = requests.delete(f'{app_url}/api/users/{data_created_user["id"]}')
    assert delete_response.status_code == HTTPStatus.OK


@pytest.mark.usefixtures("fill_test_data")
def test_users_no_duplicates(users):
    users_ids = [user["id"] for user in users]
    assert len(users_ids) == len(set(users_ids))


@pytest.mark.usefixtures("fill_test_data")
def test_users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK

    user_list = response.json()['items']
    for user in user_list:
        User.model_validate(user)


def test_user(app_url, fill_test_data):
    for user_id in (fill_test_data[0], fill_test_data[-1]):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK
        user = response.json()
        User.model_validate(user)


def test_user_nonexistent_values(app_url, user_id_too_much):
    response = requests.get(f"{app_url}/api/users/{user_id_too_much}")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_user(app_url, data_create_user):
    response = requests.post(f"{app_url}/api/users", json=data_create_user)
    assert response.status_code == HTTPStatus.CREATED
    user = response.json()
    User.model_validate(user)


def test_update_user(app_url, data_created_user, delete_created_user):
    new_user = {
        "email": "email@test.com",
        "first_name": "Thom",
        "last_name": "Yorke",
        "avatar": "https://reqres.in/img/faces/22-image.jpg"
    }
    response = requests.patch(f"{app_url}/api/users/{data_created_user['id']}", json=new_user)
    assert response.status_code == HTTPStatus.OK
    user = response.json()
    UserUpdate.model_validate(user)
    for key in new_user.keys():
        new_user[key] != data_created_user[key]
        new_user[key] != user[key]


def test_delete_user(app_url, data_created_user):
    response = requests.delete(f"{app_url}/api/users/{data_created_user['id']}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()['message'] == 'User deleted'

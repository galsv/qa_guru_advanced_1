import pytest
import requests
from http import HTTPStatus
from app.models.user import User, UserUpdate
from tests.models.user import User as TestUser


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
def data_create_user(app_url, fake_data) -> TestUser:
    create_user = TestUser(
        email=fake_data.email(),
        first_name=fake_data.first_name(),
        last_name=fake_data.last_name(),
        avatar=fake_data.image_url()
    )
    yield create_user
    delete_response = requests.delete(
        f'{app_url}/api/users/{get_user_id_by_email(app_url, create_user.email)}')
    assert delete_response.status_code == HTTPStatus.OK


@pytest.fixture
def data_created_user(app_url, fake_data) -> User:
    created_user = TestUser(
        email=fake_data.email(),
        first_name=fake_data.first_name(),
        last_name=fake_data.last_name(),
        avatar=fake_data.image_url()
    )
    response_created = requests.post(f"{app_url}/api/users", json=created_user.model_dump(mode='json'))
    assert response_created.status_code == HTTPStatus.CREATED
    created_user = User(**response_created.json())
    return created_user


@pytest.fixture
def delete_created_user(app_url, data_created_user: User):
    yield
    delete_response = requests.delete(f'{app_url}/api/users/{data_created_user.id}')
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
    response = requests.post(f"{app_url}/api/users", json=data_create_user.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.CREATED
    user = response.json()
    User.model_validate(user)


def test_update_user(app_url, fake_data, data_created_user, delete_created_user):
    new_user = TestUser(
        email=fake_data.email(),
        first_name=fake_data.first_name(),
        last_name=fake_data.last_name(),
        avatar=fake_data.image_url()
    )
    new_user_json = new_user.model_dump(mode='json')
    response = requests.patch(f"{app_url}/api/users/{data_created_user.id}", json=new_user_json)
    assert response.status_code == HTTPStatus.OK
    user = response.json()
    UserUpdate.model_validate(user)
    created_user_json = data_created_user.model_dump(mode='json')
    for key in new_user_json.keys():
        new_user_json[key] != created_user_json[key]
        new_user_json[key] == user[key]


def test_delete_user(app_url, data_created_user):
    response = requests.delete(f"{app_url}/api/users/{data_created_user.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()['message'] == 'User deleted'
    assert requests.get(f"{app_url}/api/users/{data_created_user.id}").status_code == HTTPStatus.NOT_FOUND

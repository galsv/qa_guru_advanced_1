import math
import pytest
import requests
import itertools
from http import HTTPStatus
from models.user import User


def paginate(total_items: int, page_size: int, total_pages: int) -> list[tuple]:
    pages = []
    print(page_size, total_pages)
    for page_number in range(1, total_pages + 1):
        start_index = (page_number - 1) * page_size
        end_index = min(start_index + page_size, total_items)
        items_on_page = end_index - start_index
        pages.append((total_items, page_number, items_on_page, total_pages))
    return pages


def pagination_data(total: int) -> list[tuple]:
    sizes = [1, total // 2, total // 3, total]
    pages = [math.ceil(total / i) for i in sizes]
    print(list(zip(sizes, pages)))
    return list(itertools.chain.from_iterable(
        [paginate(total, size, page) for size, page in zip(sizes, pages)]
    )) + [(total, 2, total+1, 1)]


@pytest.fixture(scope='class')
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()['items']


def test_users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK

    get_users = response.json()['items']
    for user in get_users:
        User.model_validate(user)


def test_users_no_duplicates(users):
    users_ids = [user["id"] for user in users]
    assert len(users_ids) == len(set(users_ids))


@pytest.mark.parametrize("user_id", [1, 6, 12])
def test_user(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.OK

    user = response.json()
    User.model_validate(user)


@pytest.mark.parametrize("user_id", [13])
def test_user_nonexistent_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize('total, page, size, pages', pagination_data(12))
def test_users_pagination_positive(app_url, total, page, size, pages):
    response = requests.get(f"{app_url}/api/users/", params=dict(page=page, size=size))
    assert response.status_code == HTTPStatus.OK
    response_body = response.json()
    assert response_body['total'] == total
    assert response_body['page'] == page
    assert response_body['pages'] == pages
    assert response_body['size'] == size


@pytest.mark.parametrize("size", [0, -1])
def test_users_pagination_negative(app_url, size):
    response = requests.get(f"{app_url}/api/users/?size={size}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    errors = response.json()['detail']
    assert any('Input should be greater than or equal to 1' in error['msg'] for error in errors)
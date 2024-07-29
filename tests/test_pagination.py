import math

import pytest
import requests
import itertools
from http import HTTPStatus


@pytest.fixture(scope='class')
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()['items']


def paginate(total_items: int, page_size: int, total_pages: int) -> list[tuple]:
    pages = []
    for page_number in range(1, total_pages + 1):
        start_index = (page_number - 1) * page_size
        end_index = min(start_index + page_size, total_items)
        items_on_page = end_index - start_index
        pages.append((total_items, page_number, items_on_page, total_pages))
    return pages


def pagination_data(total: int) -> list[tuple]:
    sizes = [1, total // 2, total // 3, total]
    pages = [math.ceil(total / i) for i in sizes]
    return list(itertools.chain.from_iterable(
        [paginate(total, size, page) for size, page in zip(sizes, pages)]
    )) + [(total, 2, total+1, 1)]


@pytest.mark.parametrize('total, page, size, pages', pagination_data(user_length()))
def test_users_pagination_positive(app_url, total, page, size, pages):
    response = requests.get(f"{app_url}/api/users/", params=dict(page=page, size=size))
    assert response.status_code == HTTPStatus.OK
    response_body = response.json()
    assert response_body['total'] == total
    assert response_body['page'] == page
    assert response_body['pages'] == pages
    assert response_body['size'] == size


def test_users_pagination_different_page(app_url, users):
    total = len(users)
    size = math.ceil(total / 2)
    first_page = requests.get(f"{app_url}/api/users/", params=dict(page=1, size=size))
    second_page = requests.get(f"{app_url}/api/users/", params=dict(page=2, size=size))
    assert first_page.status_code == HTTPStatus.OK
    assert second_page.status_code == HTTPStatus.OK
    first_page_items = first_page.json()['items']
    second_page_items = second_page.json()['items']
    assert any(x != y for x, y in zip(first_page_items, second_page_items))


@pytest.mark.parametrize("size", [0, -1])
def test_users_pagination_negative(app_url, size):
    response = requests.get(f"{app_url}/api/users/?size={size}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    errors = response.json()['detail']
    assert any('Input should be greater than or equal to 1' in error['msg'] for error in errors)


def test_users_no_duplicates(users):
    users_ids = [user["id"] for user in users]
    assert len(users_ids) == len(set(users_ids))

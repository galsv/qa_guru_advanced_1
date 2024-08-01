import os
import requests
import dotenv
import pytest
import json
from faker import Faker


@pytest.fixture(scope='session', autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope='session')
def app_url():
    return os.getenv("APP_URL")


@pytest.fixture(scope="session")
def fake_data():
    return Faker()


@pytest.fixture(scope="module")
def fill_test_data(app_url):
    with open("users.json") as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = requests.post(f"{app_url}/api/users/", json=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")


failed_tests_counter = 0


# Skip all remaining tests if the first three tests fail
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    global failed_tests_counter

    if result.when == "call" and result.failed:
        failed_tests_counter += 1


@pytest.fixture(autouse=True)
def check_fail_threshold():
    if failed_tests_counter >= 3:
        pytest.skip("Skipping test because the fail threshold has been reached")


# The test_smoke.py should run first
def pytest_collection_modifyitems(session, config, items):
    smoke_tests = [item for item in items if "test_smoke.py" in item.nodeid]
    other_tests = [item for item in items if "test_smoke.py" not in item.nodeid]

    items[:] = smoke_tests + other_tests

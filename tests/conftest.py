import os

import dotenv
import pytest


@pytest.fixture(scope='session', autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope='session')
def app_url():
    return os.getenv("APP_URL")


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

import socket
import pytest
import requests

from http import HTTPStatus
from urllib.parse import urlparse
from models.app_status import AppStatus


@pytest.fixture
def host_port(app_url):
    parsed_url = urlparse(app_url)
    host = parsed_url.hostname
    port = parsed_url.port
    return host, port


def test_resource_availability(host_port):
    host, port = host_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((host, port))
        available = True
    except (socket.timeout, ConnectionRefusedError):
        available = False
    finally:
        sock.close()
    assert available, f"Resource at {host}:{port} is not available"


def test_port_is_open(host_port):
    host, port = host_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    assert result == 0, f"Port {port} on host {host} is not open"


def test_check_users_status(app_url):
    response = requests.get(f'{app_url}/api/status')
    users_status = response.json()
    AppStatus.model_validate(response.json())
    assert response.status_code == HTTPStatus.OK, f'HTTPS Status code is not OK, it is {response.status_code}'
    assert users_status['users'] is True, 'Users did not add'

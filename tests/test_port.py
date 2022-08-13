import pytest
import pytest_subprocess

import helper
from helper import mock_hub, MockHub
from uhubctl import Hub, Port


def test_manual_port_creation():
    port_number = 1
    hub_path = "1"

    hub = Hub(hub_path, enumerate_ports=False)
    port = Port(hub, port_number)

    assert port.port_number == port_number


def test_port_status(mock_hub: MockHub, fp: pytest_subprocess.FakeProcess):
    for port in mock_hub.ports:
        mock_hub.cmd(fp, port.port_number)
        assert port.status is True

        mock_hub.cmd(fp, port.port_number, False)
        port.status = False

        mock_hub.cmd(fp, port.port_number)
        assert port.status is False

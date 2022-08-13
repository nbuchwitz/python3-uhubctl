import pytest
import pytest_subprocess

import helper
from helper import MockHub, mock_hub
from uhubctl import Hub

def test_empty_hub():
    hub_path = "1-2"
    hub = Hub(hub_path, enumerate_ports=False)

    assert hub.path == hub_path
    assert hub.ports == []

def test_multiple_manual_ports():
    hub_path = "1-2"
    hub = Hub(hub_path, enumerate_ports=False)

    hub.add_port(1)

    assert len(hub.ports) == 1

    hub.add_ports(2,10)

    assert len(hub.ports) == 10



def test_port_enumeration(mock_hub: MockHub, fp: pytest_subprocess.FakeProcess):
    mock_hub.cmd(fp)
    mock_hub.discover_ports()

    assert len(mock_hub.ports) == 5

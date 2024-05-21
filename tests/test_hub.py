import pytest
import pytest_subprocess

import helper
from helper import MockHub, mock_hub

import uhubctl
from uhubctl import Hub


def test_empty_hub():
    hub_path = "1-2"
    hub = Hub(hub_path, enumerate_ports=False)

    assert hub.path == hub_path
    assert hub.ports == []


def test_wrong_or_missing_parameter():
    with pytest.raises(TypeError):
        Hub()

    hub = Hub(1)
    assert hub.path == "1"


def test_multiple_manual_ports():
    hub_path = "1-2"
    hub = Hub(hub_path, enumerate_ports=False)

    hub.add_port(1)

    assert len(hub.ports) == 1

    hub.add_ports(2, 10)

    assert len(hub.ports) == 10


def test_str():
    hub_path = "1-2"
    hub = Hub(hub_path, enumerate_ports=False)

    assert str(hub) == f"USB Hub {hub_path}"


def test_port_enumeration(mock_hub: MockHub, fp: pytest_subprocess.FakeProcess):
    mock_hub.cmd(fp, n_arg=False)
    mock_hub.discover_ports()

    assert len(mock_hub.ports) == 5


def test_no_devices(fp: pytest_subprocess.FakeProcess):
    fp.register(["uhubctl", "-N"], stdout=["No compatible devices detected!".encode()])
    fp.register(["uhubctl", "-v"], stdout="2.5.0")

    hubs = uhubctl.discover_hubs()

    assert hubs == []


def test_find_port(mock_hub: MockHub, fp: pytest_subprocess.FakeProcess):
    mock_hub.cmd(fp, n_arg=False)
    mock_hub.discover_ports()

    assert mock_hub.find_port(1) is not None
    assert mock_hub.find_port(10) is None

from random import randint
import pytest
import pytest_subprocess

import helper
from helper import mock_hub, MockHub
from uhubctl import Hub, Port


@pytest.fixture
def demo_hub():
    return Hub("1", enumerate_ports=False)


@pytest.mark.parametrize("port_number", [randint(1, 20)])
def test_str(demo_hub: Hub, port_number: int):
    port = Port(demo_hub, port_number)

    assert str(port) == f"USB Port {demo_hub.path}.{port_number}"


@pytest.mark.parametrize("port_number", [randint(1, 20)])
def test_manual_port_creation(demo_hub: Hub, port_number: int):
    port = Port(demo_hub, port_number)

    assert port.port_number == port_number


def test_wrong_or_missing_parameter(demo_hub: Hub):
    with pytest.raises(TypeError):
        Port()

    with pytest.raises(TypeError):
        Port(demo_hub)

    port = Port(demo_hub, "1")
    assert port.port_number == 1

    with pytest.raises(ValueError):
        Port(demo_hub, "a")


def test_port_status(mock_hub: MockHub, fp: pytest_subprocess.FakeProcess):
    for port in mock_hub.ports:
        mock_hub.cmd(fp, port.port_number)
        assert port.status is True

        mock_hub.cmd(fp, port.port_number, False)
        port.status = False

        mock_hub.cmd(fp, port.port_number)
        assert port.status is False


def test_port_from_path():
    mock_data = [("1", 2), ("2-1", 1), ("1-2.3.1", 5)]
    for element in mock_data:
        path, port_number = element

        port = Port.from_path(f"{path}.{port_number}")

        assert port.hub.path == path
        assert port.port_number == port_number


def test_device_data(mock_hub: MockHub, fp: pytest_subprocess.FakeProcess):
    port_number = 1
    vendor_id = 0xDEAD
    product_id = 0xBEEF
    description = "Some fancy USB device"

    port = Port(mock_hub, port_number)

    mock_hub.register_port_details(fp, port_number)
    assert port.description(cached_results=False) is None

    mock_hub.register_port_details(fp, port_number)
    assert port.vendor_id(cached_results=False) is None

    mock_hub.register_port_details(fp, port_number)
    assert port.product_id(cached_results=False) is None

    mock_hub.register_port_details(fp, port_number, vendor_id, product_id, description)
    assert port.description(cached_results=False) == description
    assert port.vendor_id(cached_results=True) == vendor_id
    assert port.product_id(cached_results=True) == product_id

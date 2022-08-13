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

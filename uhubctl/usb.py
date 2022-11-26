"""Representation classes and helper functions"""
import re
from typing import List, Optional

from .utils import _uhubctl


def discover_hubs() -> List["Hub"]:
    """
    Return list of all by uhubctl supported USB hubs with their ports

    Returns:
        List of hubs

    """
    hubs = []

    pattern = re.compile(r"Current status for hub ([\.\d-]+)")

    for line in _uhubctl():
        regex = pattern.match(line)

        if regex:
            hub = Hub(regex.group(1), enumerate_ports=True)
            hubs.append(hub)

    return hubs


class Hub:
    """
    USB hub representation from uhubctl
    """

    def __init__(self, path: str, enumerate_ports: bool = False) -> None:
        """
        Create new hub instance

        Arguments:
            path: USB hub path identifier
            enumerate_ports: Automatically enumerate ports
        """
        self.path: str = str(path)
        self.ports: List[Port] = []

        if enumerate_ports:
            self.discover_ports()

    def add_port(self, port_number: int) -> "Port":
        """
        Add port to hub by port number

        Arguments:
            port_number: Indentification number of port

        Returns:
            Port

        """
        port = Port(self, port_number)
        self.ports.append(port)

        return port

    def add_ports(self, first_port: int, last_port: int):
        """
        Add multiple ports to hub

        Arguments:
            first_port: First port's indentification number
            last_port: Last port's ndentification number
        """
        for port_number in range(first_port, last_port + 1):
            self.add_port(port_number)

    def find_port(self, port_number: int) -> Optional["Port"]:
        """
        Find port by port number

        Arguments:
            port_number: Identification number of port to find

        Returns:
            Port or None
        """

        for port in self.ports:
            if port.port_number == int(port_number):
                return port

        return None

    def discover_ports(self) -> None:
        """
        Discover ports for this hub instance
        """
        pattern = re.compile(r"  Port (\d+): \d{4} ")

        for line in _uhubctl(["-l", self.path]):
            regex = pattern.match(line)

            if regex:
                port = Port(self, regex.group(1))
                self.ports.append(port)

    def __str__(self) -> str:
        return f"USB Hub {self.path}"


class Port:
    """
    USB port representation from uhubctl
    """

    def __init__(self, hub: Hub, port_number: int):
        """
        Create new port instance

        Arguments:
            hub: Hub to attach port to
            port_number: Number of port to create

        """
        self.hub = hub
        self.port_number = int(port_number)

    @property
    def status(self) -> bool:
        """
        Port power status
        """
        status = None
        pattern = re.compile(
            rf"  Port {self.port_number}: \d{{4}} (power|off|indicator)"
        )

        args = ["-l", self.hub.path, "-p", str(self.port_number)]
        for line in _uhubctl(args):
            reg = pattern.match(line)

            if reg:
                status = reg.group(1) == "power"

        if status is None:
            raise Exception()

        return status

    @status.setter
    def status(self, status: bool) -> None:
        args = ["-l", self.hub.path, "-p", str(self.port_number), "-a"]

        if status:
            args.append("on")
        else:
            args.append("off")

        _uhubctl(args)

    def __str__(self) -> str:
        return f"USB Port {self.hub.path}.{self.port_number}"

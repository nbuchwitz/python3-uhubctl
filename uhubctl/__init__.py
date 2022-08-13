"""Wrapper module for uhubctl"""

import re
import subprocess
from typing import List, Optional

UHUBCTL_BINARY = "uhubctl"


def _uhubctl(args: list = None) -> list:
    cmd = UHUBCTL_BINARY.split(" ")

    if args is not None:
        cmd += args

    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        stdout = result.stdout.decode()

        return stdout.split('\n')
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode()

        if stderr.startswith("No compatible devices detected"):
            return []

        raise Exception(f"uhubctl failed: {stderr}") from exc


def discover_hubs():
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
        self.path: str = path
        self.ports: List[Port] = []

        if enumerate_ports:
            self.discover_ports()

    def add_port(self, port_number: int) -> 'Port':
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

    def add_ports(self, port_start: int, port_end: int):
        """
        Add multiple ports to hub

        Arguments:
            port_start: First port's indentification number
            port_end: Last port's ndentification number
        """
        for port_number in range(port_start, port_end):
            self.add_port(port_number)

    def find_port(self, port_number: int) -> Optional['Port']:
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
        pattern = re.compile(r"  Port (\d+): \d{4} (power|off)")

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
        pattern = re.compile(fr"  Port {self.port_number}: \d{{4}} (power|off)")

        args = ["-l", self.hub.path, "-p", str(self.port_number)]
        for line in _uhubctl(args):
            reg = pattern.match(line)

            if reg:
                status = (reg.group(1) == "power")

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

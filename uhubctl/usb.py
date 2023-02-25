"""Representation classes and helper functions"""
import re
from typing import List, Optional

from .utils import UHubCtl


def discover_hubs() -> List["Hub"]:
    """
    Return list of all by uhubctl supported USB hubs with their ports

    Returns:
        List of hubs

    """
    hubs = []

    pattern = re.compile(r"Current status for hub ([\.\d-]+)")

    for line in UHubCtl.exec():
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

        for line in UHubCtl.exec(["-l", self.path], description=True):
            regex = pattern.match(line)

            if regex:
                # create Port object and pre-populate cache with line from autodiscovery
                port = Port(self, regex.group(1), cache=line)
                self.ports.append(port)

    def __str__(self) -> str:
        return f"USB Hub {self.path}"


class Port:
    """
    USB port representation from uhubctl
    """

    PORT_PATTERN = re.compile(
        r"  Port (?P<port>\d): \d{4} (?P<status>[a-z ]+)\s?(\[(?:(?P<vid>[a-f0-9]{4}):(?P<pid>[a-f0-9]{4})\s?(?P<description>.*)?)\])?"
    )

    def __init__(self, hub: Hub, port_number: int, cache: str = None):
        """
        Create new port instance

        Arguments:
            hub: Hub to attach port to
            port_number: Number of port to create

        """
        self.hub = hub
        self.port_number = int(port_number)
        self._cache = cache

    @property
    def status(self) -> bool:
        """
        Port power status
        """
        status = None

        args = ["-l", self.hub.path, "-p", str(self.port_number)]
        for line in UHubCtl.exec(args):
            reg = self.PORT_PATTERN.match(line)

            if reg:
                if reg.group("port") != self.port_number:
                    continue
                status = "power" in reg.group("status")

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

        UHubCtl.exec(args)

    def __attribute(self, name: str, cache: bool = True, result_filter: callable = None) -> str:
        """
        Get attribute from regexp parsed status string
        """

        if name not in ("port", "status", "vid", "pid", "description"):
            raise AttributeError(name)

        # use cache for port details if possible (fetching is slow)
        if cache and self._cache is not None:
            lines = [self._cache]
        else:
            args = ["-l", self.hub.path, "-p", str(self.port_number)]
            lines = UHubCtl.exec(args, description=True)

        for line in lines:
            reg = self.PORT_PATTERN.match(line)

            if reg:
                if int(reg.group("port")) != self.port_number:
                    continue

                self._cache = line

                if callable(result_filter):
                    return result_filter(reg.group(name))
                else:
                    return reg.group(name)

        return None

    def description(self, cached_results=True) -> str:
        """
        Attached device description

        Arguments:
            cached_results (bool): Use cached results instead of querying every time

        Return:
            Device description of the attached device
        """

        return self.__attribute("description", cached_results)

    def vendor_id(self, cached_results=True) -> int:
        """
        Attached device USB vendor id

        Arguments:
            cached_results (bool): Use cached results instead of querying every time

        Return:
            USB vendor id of the attached device
        """

        return self.__attribute("vid", cached_results, lambda x: int(x, 16) if x is not None else None)

    def product_id(self, cached_results=True) -> int:
        """
        Attached device USB product id

        Arguments:
            cached_results (bool): Use cached results instead of querying every time

        Return:
            USB product id of the attached device
        """

        return self.__attribute("pid", cached_results, lambda x: int(x, 16) if x is not None else None)

    @staticmethod
    def from_path(path: str):
        """
        Create new port instance from USB path

        Arguments:
            path: USB path

        Returns:
            Port
        """
        hub_path, port_id = path.rsplit(".", maxsplit=1)

        hub = Hub(hub_path, enumerate_ports=False)
        port = hub.add_port(port_id)

        return port

    def __str__(self) -> str:
        return f"USB Port {self.hub.path}.{self.port_number}"

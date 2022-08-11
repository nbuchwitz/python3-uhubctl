import re
import subprocess

UHUBCTL_BINARY = "uhubctl"


def __uhubctl(args: list = []) -> list:
    cmd = UHUBCTL_BINARY.split(" ") + args
    result = subprocess.run(cmd, capture_output=True)
    stdout = result.stdout.decode()

    if result.returncode != 0:
        stderr = result.stderr.decode()

        raise Exception(f"uhubctl failed: {stderr}")

    return stdout.split('\n')


def discover_hubs():
    hubs = []

    pattern_hub = re.compile("Current status for hub ([\.\d-]+)")
    pattern_port = re.compile("  Port (\d+): \d{4} (power|off)")

    for line in __uhubctl():
        reg_hub = pattern_hub.match(line)
        reg_port = pattern_port.match(line)

        if reg_hub:
            hub = Hub(reg_hub.group(1))
            hubs.append(hub)
        elif reg_port:
            # assume that the port is the last detected one
            hub = hubs[-1]

            if not hub:
                continue

            port = Port(hub, reg_port.group(1))
            hub.ports.append(port)

    return hubs


class Hub:
    def __init__(self, path: str) -> None:
        self.path = path
        self.ports = []

    def add_port(self, port_number: int) -> 'Port':
        port = Port(self, port_number)
        self.ports.append(port)

        return port

    def add_ports(self, port_start: int, port_end: int):
        for port_number in range(port_start, port_end):
            self.add_port(port_number)

    def __str__(self) -> str:
        return f"USB Hub {self.path}"


class Port:
    def __init__(self, hub: Hub, port_number: int):
        self.hub = hub
        self.port_number = port_number

    @property
    def status(self) -> bool:
        status = None
        pattern = re.compile(f"  Port {self.port_number}: \d{{4}} (power|off)")

        args = ["-l", self.hub.path, "-p", self.port_number]
        for line in __uhubctl(args):
            reg = pattern.match(line)

            if reg:
                status = (reg.group(1) == "power")

        if status is None:
            raise Exception()

        return status

    @status.setter
    def status(self, status: bool) -> None:
        args = ["-l", self.hub.path, "-p", self.port_number, "-a"]

        if status:
            args.append("on")
        else:
            args.append("off")

        __uhubctl(args)

    def __str__(self) -> str:
        return f"USB Port {self.hub.path}.{self.port_number}"

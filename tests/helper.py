import os
import sys

import pytest
import pytest_subprocess

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from uhubctl import *

class MockHub(Hub):
    def __init__(self, path: str, num_ports: int = 5) -> None:
        self.path = path
        self.num_ports = num_ports
        self.status = []

        # initialize status
        for _ in range(self.num_ports):
            self.status.append(True)

        super().__init__(path, False)

    def __stdout(self, prefix: str = "Current", port_filter: int = None):
        stdout = [
            f"{prefix} status for hub {self.path} [0424:9512, USB 2.00, {self.num_ports} ports, ppps]".encode()]

        for idx in range(self.num_ports):
            if port_filter is not None and idx+1 != int(port_filter):
                continue

            stdout.append(f"  Port {idx+1}: 0100 {self.__power_status(idx)}".encode())

        return stdout

    def __status(self, status: bool):
        if status:
            return "power"
        else:
            return "off"

    def __power_status(self, port_number: int):
        assert port_number <= self.num_ports

        return self.__status(self.status[port_number])

    def cmd(self, fp: pytest_subprocess.FakeProcess, port_number: int = None, new_status: bool = None) -> None:
        if port_number is not None:
            assert port_number <= self.num_ports

        cmd = ["uhubctl", "-N", "-l", str(self.path)]
        stdout = self.__stdout(port_filter=port_number)

        if port_number is not None:
            cmd += [ "-p", str(port_number)]

        if new_status is not None:
            self.status[port_number] = new_status

            cmd.append("-a")
            cmd.append(self.__status(new_status))

            stdout.append("Sent power on request".encode())
            stdout += self.__stdout("New", port_filter=port_number)

        fp.register(cmd, stdout=stdout)

@pytest.fixture
def mock_hub():
    path = "1-2"
    num_ports = 5
    hub = MockHub(path, num_ports)

    return hub
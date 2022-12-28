"""Utilities around uhubctl binary"""
import subprocess

from packaging import version

UHUBCTL_BINARY = "uhubctl"


class UHubCtl:
    _version = None

    @classmethod
    def version(cls) -> str:
        if cls._version is None:
            cmd = UHUBCTL_BINARY.split(" ")
            cmd.append("-v")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            cls._version = result.stdout.split("-", maxsplit=1)[0]

        return cls._version

    @classmethod
    def exec(cls, args: list = None) -> list:
        cmd = UHUBCTL_BINARY.split(" ")

        if version.parse(cls.version()) > version.parse("2.3.0"):
            cmd.append("-N")

        if args is not None:
            cmd += args

        try:
            result = subprocess.run(cmd, capture_output=True, check=True)
            stdout = result.stdout.decode()

            return stdout.split("\n")
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode()

            if stderr.startswith("No compatible devices detected"):
                return []

            raise Exception(f"uhubctl failed: {stderr}") from exc

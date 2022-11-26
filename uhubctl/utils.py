"""Utilities around uhubctl binary"""
import subprocess

UHUBCTL_BINARY = "uhubctl"


def _uhubctl(args: list = None) -> list:
    cmd = UHUBCTL_BINARY.split(" ")
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

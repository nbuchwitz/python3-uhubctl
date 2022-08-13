import pytest

import helper


def test_uhubctl_binary_invalid():
    import uhubctl
    uhubctl.utils.UHUBCTL_BINARY = "invalid-uhubctl"

    with pytest.raises(Exception):
        uhubctl.discover_hubs()


def test_uhubctl_binary_echo():
    import uhubctl
    uhubctl.utils.UHUBCTL_BINARY = "/bin/echo"

    assert uhubctl.discover_hubs() == []
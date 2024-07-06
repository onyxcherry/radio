import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--realdb", action="store_true", default=False, help="run tests with real db"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "realdb: mark test which needs real db")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--realdb"):
        return
    skip_realdb = pytest.mark.skip(reason="need --realdb option to run")
    for item in items:
        if "realdb" in item.keywords:
            item.add_marker(skip_realdb)
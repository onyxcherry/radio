import pytest

from .bootstrap import bootstrap_di
from .fixtures.reset import reset_db_fixt, reset_events_fixt  # noqa


def pytest_addoption(parser):
    parser.addoption(
        "--realdb", action="store_true", default=False, help="run tests with real db"
    )
    parser.addoption(
        "--realmsgbroker",
        action="store_true",
        default=False,
        help="run tests with real message broker",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "realdb: mark test which needs real db")
    config.addinivalue_line(
        "markers", "realmsgbroker: mark test which needs real message broker"
    )

    REAL_DB = config.getoption("realdb")
    REAL_MSG_BROKER = config.getoption("realmsgbroker")
    bootstrap_di(real_db=REAL_DB, real_msg_broker=REAL_MSG_BROKER)


def pytest_collection_modifyitems(config, items):
    REAL_DB = config.getoption("realdb")
    REAL_MSG_BROKER = config.getoption("realmsgbroker")

    if all([REAL_DB, REAL_MSG_BROKER]):
        return

    skip_realdb = pytest.mark.skip(reason="need --realdb option to run")
    skip_realmsgbroker = pytest.mark.skip(reason="need --realmsgbroker option to run")
    for item in items:
        if "realdb" in item.keywords and REAL_DB is False:
            item.add_marker(skip_realdb)
        if "realmsgbroker" in item.keywords and REAL_MSG_BROKER is False:
            item.add_marker(skip_realmsgbroker)

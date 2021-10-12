import os.path

import pytest


@pytest.fixture
def granule_directory():
    test_directory = os.path.dirname(__file__)
    return os.path.join(test_directory, "data")

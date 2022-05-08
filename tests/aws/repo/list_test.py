import pytest

from pacu.aws.repo.list import list_resources


def test_list():
    list_resources(profile='me')
import pytest
from pacu.aws.repo.ingest import ingest


def test_ingest():
    ingest('me', ['iam'])
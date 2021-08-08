import configparser
from pathlib import Path

import pytest

from conftest import run_validator_for_test_file
from flake8_future_annotations.checker import FutureAnnotationsChecker

ALL_TEST_FILES = [str(filepath) for filepath in Path("tests/test_files").glob("*.py")]


def test_version() -> None:
    config = configparser.ConfigParser()
    config.read("setup.cfg")
    assert config["metadata"]["version"] == FutureAnnotationsChecker.version


@pytest.mark.parametrize("filepath", ALL_TEST_FILES)
def test_ok_cases_produces_no_errors(filepath: str) -> None:
    if "ok" in filepath:
        errors = run_validator_for_test_file(str(filepath))

        assert len(errors) == 0, (str(filepath), errors)


@pytest.mark.parametrize("filepath", ALL_TEST_FILES)
def test_file_missing_future_import(filepath: str) -> None:
    if "ok" not in filepath:
        errors = run_validator_for_test_file(str(filepath))

        assert len(errors) == 1, (str(filepath), errors)

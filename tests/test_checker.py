import configparser

from conftest import run_validator_for_test_file
from flake8_future_annotations.checker import FutureAnnotationsChecker


def test_version() -> None:
    config = configparser.ConfigParser()
    config.read("setup.cfg")
    assert config["metadata"]["version"] == FutureAnnotationsChecker.version


def test_ok_cases_produces_no_errors() -> None:
    errors = run_validator_for_test_file("ok.py")
    assert len(errors) == 0


def test_file_missing_future_import() -> None:
    errors = run_validator_for_test_file("error.py")
    assert len(errors) == 1

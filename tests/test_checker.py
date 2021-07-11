import configparser

from conftest import run_validator_for_test_file
from flake8_future_annotations.checker import FutureAnnotationsChecker


def test_version() -> None:
    config = configparser.ConfigParser()
    config.read("setup.cfg")
    assert config["metadata"]["version"] == FutureAnnotationsChecker.version


def test_ok_cases_produces_no_errors() -> None:
    errors = run_validator_for_test_file("ok.py")
    errors += run_validator_for_test_file("ok_non_simplifiable_types.py")
    errors += run_validator_for_test_file("ok_no_types.py")
    assert len(errors) == 0


def test_file_missing_future_import() -> None:
    errors = run_validator_for_test_file("error.py")
    assert len(errors) == 1


def test_multiple_files_missing_future_import() -> None:
    errors = []
    for filename in ("ok.py", "error.py", "ok.py", "error.py"):
        errors += run_validator_for_test_file(filename)

    assert len(errors) == 2

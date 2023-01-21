import configparser
from pathlib import Path

import pytest

from flake8_future_annotations.checker import FutureAnnotationsChecker
from tests.conftest import run_validator_for_test_file

ALL_TEST_FILES = [
    str(filepath)
    for filepath in Path("tests/test_files").glob("*.py")
    if "__init__.py" not in str(filepath)
]
OK_TEST_FILES = [filepath for filepath in ALL_TEST_FILES if "ok" in filepath]
ERROR_TEST_FILES = [
    filepath
    for filepath in ALL_TEST_FILES
    if "ok" not in filepath and "no_future" not in filepath
]


def test_version() -> None:
    config = configparser.ConfigParser()
    config.read("setup.cfg")
    assert config["metadata"]["version"] == FutureAnnotationsChecker.version


@pytest.mark.parametrize("filepath", OK_TEST_FILES)
def test_ok_cases_produces_no_errors(filepath: str) -> None:
    errors = run_validator_for_test_file(filepath)

    assert len(errors) == 0, (filepath, errors)


@pytest.mark.parametrize("filepath", ERROR_TEST_FILES)
def test_file_missing_future_import(filepath: str) -> None:
    [error] = run_validator_for_test_file(filepath)

    assert error[2][:5] == "FA100"


def test_no_errors_force_future_annotations() -> None:
    errors = run_validator_for_test_file(
        "tests/test_files/ok_uses_future.py", force_future_annotations=True
    )

    assert len(errors) == 0, errors


@pytest.mark.parametrize("filepath", ERROR_TEST_FILES)
def test_file_missing_future_import_with_force_future_annotations(
    filepath: str,
) -> None:
    [error] = run_validator_for_test_file(filepath, force_future_annotations=True)
    expected_code = "FA101" if "ok" in filepath else "FA100"

    assert error[2][:5] == expected_code


def test_no_future_import_uses_lowercase() -> None:
    [error] = run_validator_for_test_file(
        "tests/test_files/no_future_import_uses_lowercase.py",
        check_future_annotations=True,
    )
    expected_code = "FA102"

    assert "dict, list" in error[2]
    assert error[2][:5] == expected_code


def test_no_future_import_uses_union() -> None:
    [error] = run_validator_for_test_file(
        "tests/test_files/no_future_import_uses_union.py", check_future_annotations=True
    )
    expected_code = "FA102"

    assert "dict, list, union" in error[2]
    assert error[2][:5] == expected_code


def test_no_future_import_uses_union_inner() -> None:
    [error] = run_validator_for_test_file(
        "tests/test_files/no_future_import_uses_union_inner.py",
        check_future_annotations=True,
    )
    expected_code = "FA102"

    assert "dict, list, tuple, union" in error[2]
    assert error[2][:5] == expected_code

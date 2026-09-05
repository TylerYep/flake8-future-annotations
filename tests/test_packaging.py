from setuptools.config.pyprojecttoml import apply_configuration
from setuptools.dist import Distribution


def test_tests_package_is_not_installed() -> None:
    dist = apply_configuration(Distribution(), "pyproject.toml")
    packages = dist.packages or []

    assert "tests" not in packages
    assert not any(name.startswith("tests.") for name in packages)

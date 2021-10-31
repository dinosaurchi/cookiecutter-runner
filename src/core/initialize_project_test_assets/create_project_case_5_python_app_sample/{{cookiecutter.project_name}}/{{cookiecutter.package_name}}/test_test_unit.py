import pytest
import {{cookiecutter.package_name}}.test as temp_main


def test_exception() -> None:
    with pytest.raises(temp_main.Error2):
        temp_main.main(8)


def test_exception_2() -> None:
    with pytest.raises(temp_main.Error2):
        temp_main.main(3)

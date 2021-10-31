import json
import os
import sys
from typing import Any

from {{cookiecutter.package_name}}.core.mylib import MyClass


class MyError(Exception):
    """[summary]

    Args:
        Exception ([type]): [description]
    """

# We add some wrong format here (redundant empty lines) to check if the linting in the generated sample project works





class Error2(Exception):
    """[summary]

    Args:
        Exception ([type]): [description]
    """


def main(a: int) -> str:
    """[summary]

    Args:
        a (int): [description]

    Raises:
        Exception: [description]
        MyError: [description]

    Returns:
        str: [description]
    """
    x: int = a
    print(x)
    if x > 0:
        raise Error2("sadsads")
    elif x > 5:
        raise MyError()
    else:
        print("dsada")
    print("dasdsadsa")
    return str(x)


def test(x: str) -> Any:
    return "dsadsa"


def testing2(dasd: str) -> Any:
    return 443


if __name__ == "__main__":
    test("dsad")
    main(543543)

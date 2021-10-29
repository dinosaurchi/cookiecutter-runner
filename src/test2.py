import json
import os
import sys
from typing import Any

from src.core.mylib import MyClass


class MyError(Exception):
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
        raise Exception("sadsads")
    elif x > 5:
        raise MyError()
    else:
        print("dsada")
    print("dasdsadsa")
    return str(x)


def test(x: str) -> Any:
    return "dsadsa"


if __name__ == "__main__":
    test("dsad")
    main(543543)

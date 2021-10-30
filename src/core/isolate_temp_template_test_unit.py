import os
import pathlib
from typing import List

import pytest

from .isolate_temp_template import get_relative_path, get_valid_paths

TEST_ASSETS_DIR = str(
    pathlib.Path(pathlib.Path(__file__).parent).joinpath(
        "isolate_temp_template_test_assets"
    )
)


@pytest.mark.parametrize(
    "f_path, cur_dir, dest_dir, expected",
    [
        (
            "/dir_11/dir_12/dir_13",
            "/dir_11",
            "/dir_11/dir_14",
            "/dir_11/dir_14/dir_12/dir_13",
        )
    ],
)
def test_get_relative_path(
    f_path: str, cur_dir: str, dest_dir: str, expected: str
) -> None:
    assert (
        get_relative_path(f_path=f_path, cur_dir=cur_dir, dest_dir=dest_dir) == expected
    )


@pytest.mark.parametrize(
    "cur_dir, expected",
    [
        (
            "get_valid_paths_1",
            [
                "cookiecutter.json",
                os.path.join("{{cookiecutter.var_name}}", "test.py"),
                os.path.join("{{cookiecutter.var_name}}", ".gitignore"),
            ],
        ),
        (
            "get_valid_paths_2_with_ignored_file",
            [
                "cookiecutter.json",
                os.path.join("hooks", "pre_gen_hook.py"),
                os.path.join("{{cookiecutter.var_name}}", "test_2.py"),
                os.path.join("{{cookiecutter.var_name}}", ".gitignore"),
            ],
        ),
        (
            "get_valid_paths_3_no_gitignore",
            [
                "cookiecutter.json",
                os.path.join("hooks", "pre_gen_hook.py"),
                os.path.join("{{cookiecutter.var_name}}", "test.py"),
                os.path.join("{{cookiecutter.var_name}}", "test_2.py"),
            ],
        ),
    ],
)
def test_get_valid_paths(cur_dir: str, expected: List[str]) -> None:
    cur_dir = pathlib.Path(TEST_ASSETS_DIR).joinpath(cur_dir).absolute().__str__()
    expected = [
        pathlib.Path(cur_dir).joinpath(f_path).absolute().__str__()
        for f_path in expected
    ]
    res = get_valid_paths(cur_dir=cur_dir)
    assert sorted(res) == sorted(expected)

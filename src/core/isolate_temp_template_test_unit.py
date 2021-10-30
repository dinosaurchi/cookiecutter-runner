import pathlib
from typing import List

import pytest

from . import isolate_temp_template as test_module

TEST_ASSETS_DIR = pathlib.Path(pathlib.Path(__file__).parent).joinpath(
    "isolate_temp_template_test_assets"
)


@pytest.mark.parametrize(
    "f_path, cur_dir, dest_dir, expected",
    [
        (
            pathlib.Path.home().joinpath("dir_11", "dir_12", "dir_13"),
            pathlib.Path.home().joinpath("dir_11"),
            pathlib.Path.home().joinpath("dir_11", "dir_14"),
            pathlib.Path.home().joinpath("dir_11", "dir_14", "dir_12", "dir_13"),
        )
    ],
)
def test_get_relative_path(
    f_path: pathlib.Path,
    cur_dir: pathlib.Path,
    dest_dir: pathlib.Path,
    expected: pathlib.Path,
) -> None:
    assert (
        test_module.get_relative_path(f_path=f_path, cur_dir=cur_dir, dest_dir=dest_dir)
        == expected
    )


@pytest.mark.parametrize(
    "cur_dir, expected",
    [
        (
            pathlib.Path("get_valid_paths_1"),
            [
                pathlib.Path("cookiecutter.json"),
                pathlib.Path("{{cookiecutter.var_name}}", "test.py"),
                pathlib.Path("{{cookiecutter.var_name}}", ".gitignore"),
            ],
        ),
        (
            pathlib.Path("get_valid_paths_2_with_ignored_file"),
            [
                pathlib.Path("cookiecutter.json"),
                pathlib.Path("hooks", "pre_gen_hook.py"),
                pathlib.Path("{{cookiecutter.var_name}}", "test_2.py"),
                pathlib.Path("{{cookiecutter.var_name}}", ".gitignore"),
            ],
        ),
        (
            pathlib.Path("get_valid_paths_3_no_gitignore"),
            [
                pathlib.Path("cookiecutter.json"),
                pathlib.Path("hooks", "pre_gen_hook.py"),
                pathlib.Path("{{cookiecutter.var_name}}", "test.py"),
                pathlib.Path("{{cookiecutter.var_name}}", "test_2.py"),
            ],
        ),
    ],
)
def test_get_valid_paths(cur_dir: pathlib.Path, expected: List[pathlib.Path]) -> None:
    cur_dir = TEST_ASSETS_DIR.joinpath(cur_dir).absolute()
    expected = [cur_dir.joinpath(f_path).absolute() for f_path in expected]
    res = test_module.get_valid_paths(cur_dir=cur_dir)
    assert sorted(res) == sorted(expected)


@pytest.mark.parametrize(
    "cur_dir, expected",
    [
        (pathlib.Path("get_valid_paths_1"), True),
        (pathlib.Path("get_valid_paths_2_with_ignored_file"), True),
        (pathlib.Path("get_valid_paths_3_no_gitignore"), True),
        (pathlib.Path("invalid_cookiecutter_dir_1_no_json"), False),
        (pathlib.Path("invalid_cookiecutter_dir_2_no_dir_name"), False),
    ],
)
def test_is_valid_template_directory(
    cur_dir: pathlib.Path,
    expected: bool,
) -> None:
    cur_dir = TEST_ASSETS_DIR.joinpath(cur_dir).absolute()
    assert test_module.is_valid_template_directory(cur_dir=cur_dir) == expected


@pytest.mark.parametrize(
    "cur_dir",
    [
        pathlib.Path("not_existing_path"),
    ],
)
def test_is_valid_template_directory_error(cur_dir: pathlib.Path) -> None:
    cur_dir_path = TEST_ASSETS_DIR.joinpath(cur_dir).absolute()
    with pytest.raises(FileNotFoundError):
        test_module.is_valid_template_directory(cur_dir=cur_dir_path)

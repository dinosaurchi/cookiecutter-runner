import pathlib
import shutil
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


class Test_is_valid_template_directory:
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
    def test_normal_case(
        self,
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
    def test_error_case(self, cur_dir: pathlib.Path) -> None:
        cur_dir_path = TEST_ASSETS_DIR.joinpath(cur_dir).absolute()
        with pytest.raises(FileNotFoundError):
            test_module.is_valid_template_directory(cur_dir=cur_dir_path)


class Test_run:
    def generate_project(
        self, template_dir: pathlib.Path, cache_dir: pathlib.Path
    ) -> None:
        if not template_dir.is_dir():
            raise FileNotFoundError(template_dir)
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
        assert not cache_dir.is_dir()
        # Generate cache
        test_module.run(template_dir=template_dir, cache_dir=cache_dir)
        assert cache_dir.is_dir()

    def get_cache_dir(self, template_dir: pathlib.Path) -> pathlib.Path:
        return template_dir.parent.joinpath(str(template_dir.name) + "_cached")

    def compare_cache(
        self, cache_dir_1: pathlib.Path, cache_dir_2: pathlib.Path
    ) -> None:
        f_paths_1 = sorted(
            [str(f_path.relative_to(cache_dir_1)) for f_path in cache_dir_1.rglob("*")]
        )
        f_paths_2 = sorted(
            [str(f_path.relative_to(cache_dir_2)) for f_path in cache_dir_2.rglob("*")]
        )
        assert f_paths_1 == f_paths_2

    @pytest.mark.parametrize(
        "template_dir",
        [
            pathlib.Path("run_1_empty_hooks"),
            pathlib.Path("run_2_with_ignored_file"),
            pathlib.Path("run_3_no_gitignore"),
        ],
    )
    def test_remove_existing_cache(self, template_dir: pathlib.Path) -> None:
        # Generate project from target test template
        template_dir = TEST_ASSETS_DIR.joinpath(template_dir).absolute()
        cache_dir = self.get_cache_dir(template_dir=template_dir)
        self.generate_project(template_dir=template_dir, cache_dir=cache_dir)

        # Generate the projcet from the temporary template to a specific cache
        # It is used as a ground truth to check the next step
        temporary_template_dir = TEST_ASSETS_DIR.joinpath("run_temp_case").absolute()
        ground_truth_cache_dir = self.get_cache_dir(template_dir=temporary_template_dir)
        self.generate_project(
            template_dir=temporary_template_dir, cache_dir=ground_truth_cache_dir
        )

        # Generate another template to the same cache to check if the old cache is removed
        test_module.run(template_dir=temporary_template_dir, cache_dir=cache_dir)

        # Compare the new cache with the ground truth cache
        self.compare_cache(cache_dir_1=cache_dir, cache_dir_2=ground_truth_cache_dir)

        # Clean out the generated data
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
        assert not cache_dir.is_dir()
        if ground_truth_cache_dir.is_dir():
            shutil.rmtree(ground_truth_cache_dir)
        assert not ground_truth_cache_dir.is_dir()

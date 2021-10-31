import logging
import pathlib
import shutil
from typing import List

import pytest

from . import initialize_project as test_module

logging.basicConfig(level=logging.INFO)

TEST_ASSETS_DIR = pathlib.Path(pathlib.Path(__file__).parent).joinpath(
    "initialize_project_test_assets"
)

SAMPLES_DIR = TEST_ASSETS_DIR.joinpath("samples")


class Test_create_project:
    def check_generated_project(
        self, project_dir: pathlib.Path, has_gitignore: bool
    ) -> None:
        """Make sure the generated project has all placeholders being filled

        Args:
            project_dir (pathlib.Path): the project directory path
        """
        if has_gitignore is True:
            assert project_dir.joinpath(".gitignore").is_file()
        f_paths = [f_path.relative_to(project_dir) for f_path in project_dir.rglob("*")]
        assert len(f_paths) > 1
        for f_path in f_paths:
            assert not ("{{cookicutter." in str(f_path))
            if f_path.is_file():
                try:
                    with open(f_path, "r") as f:
                        content = f.read()
                        assert not ("{{cookiecutter." in content)
                except UnicodeDecodeError:
                    logging.warning(
                        "Skipping non-text file {f_path}".format(f_path=f_path)
                    )

    @pytest.mark.parametrize(
        "template_dir, has_gitignore, is_correct",
        [
            (pathlib.Path("create_project_case_1_empty_hooks"), True, True),
            (pathlib.Path("create_project_case_2_with_ignored_file"), True, True),
            (pathlib.Path("create_project_case_3_no_gitignore"), False, True),
            (pathlib.Path("create_project_case_4_no_cookiecutter_error"), True, False),
            (pathlib.Path("create_project_case_5_python_app_sample"), True, True),
        ],
    )
    def test_normal_case(
        self, template_dir: pathlib.Path, has_gitignore: bool, is_correct: bool
    ) -> None:
        template_dir = TEST_ASSETS_DIR.joinpath(template_dir).absolute()
        output_dir = SAMPLES_DIR.joinpath(template_dir.name)
        if is_correct is True:
            test_module.create_project(
                template_dir=template_dir,
                output_dir=output_dir,
            )
            f_paths = list(output_dir.glob("*"))
            assert len(f_paths) == 1
            self.check_generated_project(
                project_dir=f_paths[0], has_gitignore=has_gitignore
            )
        else:
            with pytest.raises(RuntimeError):
                test_module.create_project(
                    template_dir=template_dir, output_dir=output_dir
                )
        if output_dir.is_dir():
            logging.info(
                "Cleaning up generated samples directory: {output_dir}".format(
                    output_dir=output_dir
                )
            )
            shutil.rmtree(output_dir)
            shutil.rmtree(SAMPLES_DIR)


class Test_merge_commands:
    @pytest.mark.parametrize(
        "commands, merge_operator, expected",
        [
            (
                [
                    ["ls", "-l"],
                    ["python3", "test.py", "--config", "./dir"],
                    ["git", "init"],
                ],
                "&&",
                [
                    "ls",
                    "-l",
                    "&&",
                    "python3",
                    "test.py",
                    "--config",
                    "./dir",
                    "&&",
                    "git",
                    "init",
                ],
            ),
            (
                [
                    ["python2", "test4.py", "--input", "./data"],
                    ["git", "add", "."],
                ],
                ";",
                ["python2", "test4.py", "--input", "./data", ";", "git", "add", "."],
            ),
            (
                [["python2", "test4.py", "--input", "./data"]],
                "||",
                ["python2", "test4.py", "--input", "./data"],
            ),
        ],
    )
    def test_normal_case(
        self, commands: List[List[str]], merge_operator: str, expected: List[str]
    ) -> None:
        res = test_module.merge_commands(
            commands=commands, merge_operator=merge_operator
        )
        assert res == expected


class Test_install_project:
    def get_test_directory(self, project_dir: pathlib.Path) -> pathlib.Path:
        test_dir = project_dir.joinpath(".test_cache")
        if test_dir.is_dir():
            shutil.rmtree(test_dir)
        shutil.copytree(project_dir, test_dir)
        return test_dir

    def test_install_project_case_1_simple(self) -> None:
        def assert_content(f_path: pathlib.Path, expected: str) -> None:
            assert f_path.is_file()
            with open(f_path, "r") as f:
                assert f.read() == expected

        project_dir = self.get_test_directory(
            project_dir=TEST_ASSETS_DIR.joinpath("install_project_case_1_simple")
        )
        test_module.install_project(project_dir=project_dir)
        assert not project_dir.joinpath(".git").is_dir()
        assert_content(
            f_path=project_dir.joinpath("src").joinpath("default"), expected="test"
        )
        assert_content(
            f_path=project_dir.joinpath("src").joinpath("install"),
            expected="Installing\n",
        )
        assert_content(
            f_path=project_dir.joinpath("src").joinpath("lint"), expected="Linting\n"
        )
        assert_content(
            f_path=project_dir.joinpath("src").joinpath("check"), expected="Checking\n"
        )
        assert_content(
            f_path=project_dir.joinpath("src").joinpath("test"), expected="Testing\n"
        )
        if project_dir.is_dir():
            shutil.rmtree(project_dir)

import logging
import pathlib
import shutil

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
            (pathlib.Path("case_1_empty_hooks"), True, True),
            (pathlib.Path("case_2_with_ignored_file"), True, True),
            (pathlib.Path("case_3_no_gitignore"), False, True),
            (pathlib.Path("case_4_no_cookiecutter_error"), True, False),
            (pathlib.Path("case_5_python_app_sample"), True, True),
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

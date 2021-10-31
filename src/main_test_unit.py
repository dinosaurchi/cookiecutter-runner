import logging
import pathlib
import shutil
import subprocess

from . import main as test_module

logging.basicConfig(level=logging.INFO)

TEST_ASSETS_DIR = pathlib.Path(pathlib.Path(__file__).parent).joinpath(
    "main_test_assets"
)


class Test_run:
    def test_run_case_1(self) -> None:
        def assert_content(f_path: pathlib.Path, expected: str) -> None:
            assert f_path.is_file()
            with open(f_path, "r") as f:
                assert f.read() == expected

        cache_dir = TEST_ASSETS_DIR.joinpath(".test_cache")
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
        test_module.run(
            template_dir=TEST_ASSETS_DIR.joinpath("run_case_1"), output_dir=cache_dir
        )
        f_paths = list(cache_dir.glob("*"))
        assert len(f_paths) == 1
        project_dir = f_paths[0]
        assert not project_dir.joinpath(".git").is_dir()
        assert_content(
            f_path=project_dir.joinpath("testing_module").joinpath("default"),
            expected="test",
        )
        assert_content(
            f_path=project_dir.joinpath("testing_module").joinpath("install"),
            expected="Installing\n",
        )
        assert_content(
            f_path=project_dir.joinpath("testing_module").joinpath("lint"),
            expected="Linting\n",
        )
        assert_content(
            f_path=project_dir.joinpath("testing_module").joinpath("check"),
            expected="Checking\n",
        )
        assert_content(
            f_path=project_dir.joinpath("testing_module").joinpath("test"),
            expected="Testing\n",
        )
        shutil.rmtree(cache_dir)

    def test_main_entrypoint(self) -> None:
        cache_dir = TEST_ASSETS_DIR.joinpath(".test_cache")
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)

        p = subprocess.Popen(
            [
                "python3",
                pathlib.Path("src", "main.py"),
                "--template",
                TEST_ASSETS_DIR.joinpath("run_case_1"),
                "--cache",
                cache_dir,
            ]
        )
        res, _ = p.communicate()
        p.wait()
        if p.returncode != 0:
            raise RuntimeError(res.decode("utf-8"))
        shutil.rmtree(cache_dir)

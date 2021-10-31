import argparse
import logging
import pathlib
import shutil

from src.core import initialize_project, isolate_temp_template

logging.basicConfig(level=logging.INFO)


def run(template_dir: pathlib.Path, output_dir: pathlib.Path) -> None:
    """Create, install and test the project from a template

    Args:
        template_dir (pathlib.Path): template directory path
        output_dir (pathlib.Path): output directory path
    """
    isolated_template_dir = template_dir.joinpath(".template_cache")
    isolate_temp_template.run(
        template_dir=template_dir, cache_dir=isolated_template_dir
    )
    initialize_project.create_project(
        template_dir=isolated_template_dir, output_dir=output_dir
    )
    logging.info(
        "Removing isolated template directory cache at {isolated_template_dir}".format(
            isolated_template_dir=isolated_template_dir
        )
    )
    shutil.rmtree(isolated_template_dir)
    for f_path in output_dir.glob("*"):
        logging.info("Installing and testing {f_path}".format(f_path=f_path))
        initialize_project.install_project(project_dir=f_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--template", help="Cookiecutter template directory", required=True
    )
    parser.add_argument(
        "--cache",
        help="Cache directory",
        default=pathlib.Path(".", ".cookiecutter-runner_cache"),
    )
    args = parser.parse_args()
    template_dir: pathlib.Path = pathlib.Path(args.template)
    output_dir: pathlib.Path = pathlib.Path(args.output)

    run(template_dir=template_dir, output_dir=output_dir)


if __name__ == "__main__":
    main()

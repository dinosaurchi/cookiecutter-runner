import argparse
import logging
import os
import pathlib
import subprocess
from typing import List

from gitignore_parser import parse_gitignore

logging.basicConfig(level=logging.INFO)


def is_valid_template_directory(cur_dir: pathlib.Path) -> bool:
    """Check if a directory is a template directory

    Args:
        cur_dir (pathlib.Path): target template directory path

    Returns:
        bool:
        - True if having cookiecutter.json and a {{cookiecutter.var_name}} directory
        - False otherwise
    """
    if not cur_dir.joinpath("cookiecutter.json").is_file():
        return False
    f_paths = list(cur_dir.glob("*"))
    temp_dirs = [
        f_path for f_path in f_paths if f_path.name.startswith("{{cookiecutter.")
    ]
    if len(temp_dirs) != 1:
        return False
    return True


def get_not_ignored_paths(
    cur_dir: pathlib.Path, gitignore_path: pathlib.Path
) -> List[pathlib.Path]:
    """Get path not being ignored by git due to the .gitignore

    Args:
        cur_dir (pathlib.Path): directory to be considered
        gitignore_path (pathlib.Path): .gitignore path

    Returns:
        List[pathlib.Path]: list of paths in cur_dir not being ignored by git
    """
    f_paths = [f_path for f_path in cur_dir.rglob("*") if f_path.is_file()]
    if not gitignore_path.is_file():
        return list(f_paths)

    matcher = parse_gitignore(gitignore_path)
    f_paths = [
        pathlib.Path(f_path).absolute()
        for f_path in f_paths
        if matcher(f_path) is False
    ]
    return list(f_paths)


def get_valid_paths(cur_dir: pathlib.Path) -> List[pathlib.Path]:
    """Get the paths to be copied to .cache

    Args:
        cur_dir (pathlib.Path): target template directory

    Raises:
        Exception: Invalid tempalte directory

    Returns:
        List[pathlib.Path]: paths to be copied
    """
    if not is_valid_template_directory(cur_dir=cur_dir):
        raise Exception("Invalid template directory: {cur_dir}".format(cur_dir=cur_dir))

    cur_dir = cur_dir.absolute()
    f_paths = list(pathlib.Path(cur_dir).glob("*"))

    # cookiecutter.json and the hooks (optional) are added initially
    result_paths = [cur_dir.joinpath("cookiecutter.json")]
    hooks_dir_path = cur_dir.joinpath("hooks")
    if hooks_dir_path.is_dir():
        result_paths.extend(list(pathlib.Path(hooks_dir_path).rglob("*")))

    # Get the only {{cookiecutter.var_name}} directory path
    project_path = [
        f_path for f_path in f_paths if f_path.name.startswith("{{cookiecutter.")
    ][0]
    gitignore_path = project_path.joinpath(".gitignore")

    # Get paths of files not ignored by git in the template project
    not_ignored_paths = get_not_ignored_paths(
        cur_dir=project_path, gitignore_path=gitignore_path
    )
    # Append these paths to the final result
    result_paths += not_ignored_paths
    logging.info(
        "Loaded {n} not ignored paths by .gitignore".format(n=len(not_ignored_paths))
    )
    return result_paths


def get_relative_path(
    f_path: pathlib.Path, cur_dir: pathlib.Path, dest_dir: pathlib.Path
) -> pathlib.Path:
    """Return the new path of f_path when changing the working directory from cur_dir to dest_dir

    Args:
        f_path (pathlib.Path): target file path
        cur_dir (pathlib.Path): current working directory (contain the target file path)
        dest_dir (pathlib.Path): new working directory (where the f_path file will be moved to)

    Returns:
        pathlib.Path: the new path
    """
    f_path = f_path.relative_to(cur_dir)
    return dest_dir.joinpath(f_path)


def run(template_dir: pathlib.Path, cache_dir: pathlib.Path) -> None:
    """Execute the isolating process

    Args:
        template_dir (pathlib.Path): template directory path
        cache_dir (pathlib.Path): cache directory path
    """
    template_dir = template_dir.absolute()
    dir_name: str = template_dir.name
    cache_dir = cache_dir.joinpath(dir_name).absolute()

    if cache_dir.is_dir():
        logging.info("Removing existing cache {cache_dir}".format(cache_dir=cache_dir))
        p = subprocess.Popen(["rm", "-Rf", cache_dir], stdout=subprocess.PIPE)
        p.communicate()
        p.wait()

    os.makedirs(cache_dir, exist_ok=False)

    res: List[pathlib.Path] = get_valid_paths(cur_dir=template_dir)
    logging.info("Loaded {n} valid paths".format(n=len(res)))

    for f_path in res:
        dest_path = get_relative_path(
            f_path=f_path, cur_dir=template_dir, dest_dir=cache_dir
        )
        dest_dir = pathlib.Path(dest_path).parent
        os.makedirs(dest_dir, exist_ok=True)
        p = subprocess.Popen(["cp", "-Rf", f_path, dest_path], stdout=subprocess.PIPE)
        p.communicate()
        p.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--template", help="Cookiecutter template directory", required=True
    )
    args = parser.parse_args()
    template_dir: pathlib.Path = pathlib.Path(args.template)
    cache_dir: pathlib.Path = pathlib.Path(template_dir, ".template_cache")

    run(template_dir=template_dir, cache_dir=cache_dir)

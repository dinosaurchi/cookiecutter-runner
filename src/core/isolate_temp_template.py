import argparse
import logging
import os
import pathlib
import subprocess
from typing import List, Set

from gitignore_parser import parse_gitignore

logging.basicConfig(level=logging.INFO)


def is_valid_template_directory(cur_dir: str) -> bool:
    """Check if a directory is a template directory

    Args:
        cur_dir (str): target template directory path

    Returns:
        bool:
        - True if having cookiecutter.json and a {{cookiecutter.var_name}} directory
        - False otherwise
    """
    if not pathlib.Path(cur_dir).joinpath("cookiecutter.json").is_file():
        return False
    f_paths = list(pathlib.Path(cur_dir).glob("*"))
    temp_dirs = [
        f_path
        for f_path in f_paths
        if pathlib.Path(f_path).name.startswith("{{cookiecutter.")
    ]
    if len(temp_dirs) != 1:
        return False
    return True


def get_not_ignored_paths(cur_dir: str, gitignore_path: str) -> Set[str]:
    """Get path not being ignored by git due to the .gitignore

    Args:
        cur_dir (str): directory to be considered
        gitignore_path (str): .gitignore path

    Returns:
        Set[str]: set of paths in cur_dir not being ignored by git
    """
    f_paths = [
        str(f_path) for f_path in pathlib.Path(cur_dir).rglob("*") if f_path.is_file()
    ]
    if not pathlib.Path(gitignore_path).is_file():
        return set(f_paths)

    matcher = parse_gitignore(gitignore_path)
    f_paths = [
        str(pathlib.Path(f_path).absolute())
        for f_path in f_paths
        if matcher(f_path) is False
    ]
    return set(f_paths)


def get_valid_paths(cur_dir: str) -> List[str]:
    """Get the paths to be copied to .cache

    Args:
        cur_dir (str): target template directory

    Raises:
        Exception: Invalid tempalte directory

    Returns:
        List[str]: paths to be copied
    """
    if not is_valid_template_directory(cur_dir=cur_dir):
        raise Exception("Invalid template directory: {cur_dir}".format(cur_dir=cur_dir))

    cur_dir = os.path.abspath(cur_dir)
    f_paths = list(pathlib.Path(cur_dir).glob("*"))

    # cookiecutter.json and the hooks (optional) are added initially
    result_paths = [str(pathlib.Path(cur_dir).joinpath("cookiecutter.json"))]
    hooks_dir_path = str(pathlib.Path(cur_dir).joinpath("hooks"))
    if pathlib.Path(hooks_dir_path).is_dir():
        result_paths.extend(
            [str(f_path) for f_path in pathlib.Path(hooks_dir_path).rglob("*")]
        )

    # Get the only {{cookiecutter.var_name}} directory path
    project_path = [
        f_path
        for f_path in f_paths
        if pathlib.Path(f_path).name.startswith("{{cookiecutter.")
    ][0]
    gitignore_path = pathlib.Path(project_path).joinpath(".gitignore")

    # Get paths of files not ignored by git in the template project
    not_ignored_paths = get_not_ignored_paths(
        cur_dir=str(project_path), gitignore_path=str(gitignore_path)
    )
    logging.info(
        "Loaded {n} not ignored paths by .gitignore".format(n=len(not_ignored_paths))
    )
    # Append these paths to the final result
    result_paths += [
        f_path for f_path in not_ignored_paths if f_path.startswith(str(project_path))
    ]
    return result_paths


def get_relative_path(f_path: str, cur_dir: str, dest_dir: str) -> str:
    """Return the new path of f_path when changing the working directory from cur_dir to dest_dir

    Args:
        f_path (str): target file path
        cur_dir (str): current working directory (contain the target file path)
        dest_dir (str): new working directory (where the f_path file will be moved to)

    Returns:
        str: the new path
    """
    f_path = os.path.relpath(f_path, cur_dir)
    return os.path.join(dest_dir, f_path)


def run(template_dir: str, cache_dir: str) -> None:
    """Execute the isolating process

    Args:
        template_dir (str): template directory path
        cache_dir (str): cache directory path
    """
    template_dir = os.path.abspath(template_dir)
    dir_name: str = pathlib.Path(template_dir).name
    cache_dir = os.path.abspath(os.path.join(cache_dir, dir_name))

    if os.path.isdir(cache_dir):
        logging.info("Removing existing cache {cache_dir}".format(cache_dir=cache_dir))
        p = subprocess.Popen(["rm", "-Rf", cache_dir], stdout=subprocess.PIPE)
        p.communicate()
        p.wait()

    os.makedirs(cache_dir, exist_ok=False)

    res: List[str] = get_valid_paths(cur_dir=template_dir)
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
    template_dir: str = args.template
    cache_dir: str = str(pathlib.Path(template_dir, ".template_cache"))

    run(template_dir=template_dir, cache_dir=cache_dir)

import argparse
import logging
import os
import pathlib
import subprocess
from typing import List, Set

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


def get_not_ignored_paths(gitignore_path: str) -> Set[str]:
    """Get path not being ignored by git due to the .gitignore

    Args:
        gitignore_path (str): .gitignore path

    Returns:
        Set[str]: set of paths not being ignored by git
    """
    if not os.path.isfile(gitignore_path):
        return set()
    p = subprocess.Popen(
        [
            "git",
            "ls-files",
            "-c",
            "-m",
            "-o",
            "--directory",
            "--exclude-from={gitignore_path}".format(gitignore_path=gitignore_path),
        ],
        stdout=subprocess.PIPE,
    )
    res: str = p.communicate()[0].decode("utf-8")
    p.wait()
    output_paths: List[str] = res.split("\n")
    output_paths = [os.path.abspath(f_path) for f_path in output_paths]
    return set(output_paths)


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
        result_paths.append(hooks_dir_path)

    # Get the only {{cookiecutter.var_name}} directory path
    project_path = [
        f_path
        for f_path in f_paths
        if pathlib.Path(f_path).name.startswith("{{cookiecutter")
    ][0]
    gitignore_path = pathlib.Path(project_path).joinpath(".gitignore")

    # Get paths of files not ignored by git in the template project
    not_ignored_paths = get_not_ignored_paths(gitignore_path=str(gitignore_path))
    logging.info(
        "Loaded {n} not ignored paths by .gitignore".format(n=len(not_ignored_paths))
    )
    # Append these paths to the final result
    result_paths += [
        f_path for f_path in not_ignored_paths if f_path.startswith(str(project_path))
    ]
    return result_paths


def get_relative_path(f_path: str, cur_dir: str, dest_dir: str) -> str:
    f_path = os.path.relpath(f_path, cur_dir)
    return os.path.join(dest_dir, f_path)


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

    template_dir = os.path.abspath(template_dir)
    project_dir: str = os.path.join(template_dir, "{{cookiecutter.project_name}}")

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

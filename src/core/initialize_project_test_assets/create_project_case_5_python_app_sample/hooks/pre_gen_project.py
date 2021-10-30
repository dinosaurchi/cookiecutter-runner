import glob
import logging
import os
import re
import subprocess
from typing import List


def run_and_check(args: List[str], raise_error: bool) -> bool:
    p = subprocess.Popen(args)
    p.communicate()[0]
    p.wait()
    if p.returncode != 0:
        if raise_error == False:
            return False
        msg = "Failed to run {args}".format(args=" ".join(args))
        logging.debug(msg=msg)
        raise Exception(msg)
    logging.debug(msg="Successfully running {args}".format(args=" ".join(args)))
    return True


def check_name_variable(module_name: str) -> None:
    logging.debug("Checking {module_name}".format(module_name=module_name))
    # Ref: https://cookiecutter.readthedocs.io/en/1.7.2/advanced/hooks.html#example-validating-template-variables
    MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

    if not re.match(MODULE_REGEX, module_name):
        raise Exception(
            "{module_name} does not match with pattern ".format(module_name=module_name)
            + str(MODULE_REGEX)
        )


def remove_old_files_directory(excludes: List[str]) -> None:
    # Clean the output space before creating the project
    def match_excludes(f_path: str) -> bool:
        for e_path in excludes:
            if os.path.samefile(e_path, f_path):
                return True
        return False

    logging.debug("Removing old files, directories except .venv, .git and debug")
    excludes = [
        f_path for f_path in excludes if os.path.isdir(f_path) or os.path.isfile(f_path)
    ]
    file_paths = glob.glob("./*")
    for f_path in file_paths:
        if match_excludes(f_path=f_path):
            logging.debug("Skipped removing {f_path}".format(f_path=f_path))
            continue
        logging.debug("Removing {f_path}".format(f_path=f_path))
        run_and_check(args=["rm", "-R", f_path], raise_error=True)


check_name_variable(module_name="{{cookiecutter.package_name}}")
remove_old_files_directory(excludes=[".venv", ".git", "debug"])

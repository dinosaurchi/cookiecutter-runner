import logging
import pathlib
import subprocess
from typing import List

logging.basicConfig(level=logging.INFO)


def create_project(template_dir: pathlib.Path, output_dir: pathlib.Path) -> None:
    """Generate a project based on the template_dir

    Args:
        template_dir (pathlib.Path): template directory path
        output_dir (pathlib.Path): output directory path

    Raises:
        RuntimeError: project generating process failed
    """
    logging.info(
        "Creating project based on template: {template_dir}".format(
            template_dir=template_dir
        )
    )
    p = subprocess.Popen(
        [
            "cookiecutter",
            str(template_dir.absolute()),
            "--no-input",
            "--overwrite-if-exists",
            "--output-dir",
            str(output_dir.absolute()),
        ],
        stdout=subprocess.PIPE,
    )
    res, _ = p.communicate()
    p.wait()
    if p.returncode != 0:
        message = res.decode("utf-8")
        logging.error(message)
        raise RuntimeError(message)
    logging.info("Created project at: {output_dir}".format(output_dir=output_dir))


def merge_commands(commands: List[List[str]], merge_operator: str) -> List[str]:
    """Join all commands (each command is a list of strings) with a merge operator

    Args:
        commands (List[List[str]]): list of commands
        merge_operator (str): merge operator such as &&, ||, ...

    Returns:
        List[str]: a merged list of commands
    """
    res = commands[0]
    for cmd in commands[1:]:
        res.append(merge_operator)
        res.extend(cmd)
    return res

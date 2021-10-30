import logging
import os
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


if os.path.isdir(".git"):
    logging.debug(msg="Existing .git, skip initializing git")
else:
    logging.debug(msg="Git initialization for the generated project from the template")
    run_and_check(args=["git", "init"], raise_error=True)

run_and_check(args=["git", "add", "."], raise_error=True)
# We do not commit the code here, just for testing

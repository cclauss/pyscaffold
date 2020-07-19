# -*- coding: utf-8 -*-
import os
import shlex
import sys
import traceback
from os import environ
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output

IS_POSIX = os.name == "posix"

PYTHON = sys.executable
"""Same python executable executing the tests... Hopefully the one inside the virtualenv
inside tox folder. If we install packages by mistake is not a huge problem.
"""


def merge_env(other={}, **kwargs):
    """Create a dict from merging items to the current ``os.environ``"""
    env = {k: v for k, v in environ.items()}  # Clone the environ as a dict
    env.update(other)
    env.update(kwargs)
    return env


def run(*args, **kwargs):
    """Run the external command. See ``subprocess.check_output``."""
    # normalize args
    if len(args) == 1:
        if isinstance(args[0], str):
            args = shlex.split(args[0], posix=IS_POSIX)
        else:
            args = args[0]

    if args[0] in ("python", "putup", "pip", "tox", "pytest", "pre-commit"):
        raise SystemError("Please specify an executable with explicit path")

    opts = dict(stderr=STDOUT, universal_newlines=True)
    opts.update(kwargs)

    try:
        return check_output(args, **opts)
    except CalledProcessError as ex:
        traceback.print_exc()
        msg = "******************** Terminal ($? = {}) ********************\n{}"
        print(msg.format(ex.returncode, ex.output))
        raise


def sphinx_cmd(build):
    docs_dir = Path("docs")
    build_dir = docs_dir / "_build"
    doctrees = build_dir / "doctrees"
    output_dir = build_dir / build
    return f"{PYTHON} -m sphinx -b {build} -d {doctrees} {docs_dir} {output_dir}"


def run_common_tasks(tests=True, flake8=True):
    if tests:
        run(f"{PYTHON} -m pytest", env=merge_env(PYTHONPATH="src"))

    run(sphinx_cmd("doctest"))
    run(sphinx_cmd("html"))

    run(f"{PYTHON} setup.py --version")
    run(f"{PYTHON} setup.py sdist")
    run(f"{PYTHON} setup.py bdist")

    if flake8 and environ.get("COVERAGE") == "true":
        run(f"{PYTHON} -m flake8 --count")

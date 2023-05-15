# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Bootstrap file, which builds the local EDM development environment for this
    example.
"""

import getopt
import subprocess
import sys

from config import EDM_DEPS, ENV_NAME, PIP_DEPS


def bootstrap(edm_config=None, edm_token=None):
    """Create and populate dev env"""

    base_cmd = ["edm"]
    if edm_config is not None:
        print(f"Using edm configuration {edm_config}")
        base_cmd.append("-c")
        base_cmd.append(edm_config)
    if edm_token is not None:
        print("Using edm token ***")
        base_cmd.append("-t")
        base_cmd.append(edm_token)

    if ENV_NAME not in _list_edm_envs(base_cmd):
        print("Creating EDM Python environment...")
        cmd = base_cmd + ["envs", "create", ENV_NAME, "--version", "3.8", "--force"]
        subprocess.run(cmd, check=True)

        print("Installing EDM dependencies...")
        cmd = base_cmd + ["install", "-e", ENV_NAME, "-y"] + EDM_DEPS
        subprocess.run(cmd, check=True)

        print("Installing pip dependencies...")
        cmd = base_cmd + ["run", "-e", ENV_NAME, "--", "pip", "install"] + PIP_DEPS
        subprocess.run(cmd, check=True)

    print("Bootstrap complete.")
    print(f"Activating dev environment {ENV_NAME}")
    subprocess.run(["edm", "shell", "-e", ENV_NAME])


def _list_edm_envs(edm_base_cmd):
    cmd = edm_base_cmd + ["envs", "list"]
    proc = subprocess.run(
        cmd, check=True, capture_output=True, encoding="utf-8", errors="ignore"
    )
    envs = []
    for line in proc.stdout.split("\n"):
        parts = line.split()
        if len(parts) < 6:
            continue
        if parts[0] == "*":
            envs.append(parts[1])
        else:
            envs.append(parts[0])
    return envs


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "c:t:")
    edm_config = None
    edm_token = None
    for o, a in opts:
        if o == "-c":
            edm_config = a
        if o == "-t":
            edm_token = a
    bootstrap(edm_config=edm_config, edm_token=edm_token)

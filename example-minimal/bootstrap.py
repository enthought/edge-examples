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

ENV_NAME = "edge-minimal-example"
EDM_DEPS = ["click"]
PIP_DEPS = ["jupyterhub==2.2.2", "sqlalchemy<2", "dockerspawner"]


def bootstrap():
    """Create and populate dev env"""

    if ENV_NAME not in _list_edm_envs(base_cmd):
        print(f"Creating development environment {ENV_NAME}...")
        cmd = ["edm", "envs", "create", ENV_NAME, "--version", "3.8", "--force"]
        subprocess.run(cmd, check=True)

        cmd = base_cmd + ["install", "-e", ENV_NAME, "-y"] + EDM_DEPS
        subprocess.run(cmd, check=True)

        cmd = base_cmd + ["run", "-e", ENV_NAME, "--", "pip", "install"] + PIP_DEPS
        subprocess.run(cmd, check=True)

        print("Bootstrap complete.")

    else:
        print("Environment already exists; reusing.")

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
    bootstrap()

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

import subprocess

ENV_NAME = "edge-externally-hosted-example"
EDM_DEPS = ["click", "pip", "setuptools==59.8.0-1", "authlib", "flask>2", "gunicorn", "requests"]
PIP_DEPS = ["Flask-Session"]


def bootstrap():
    """Create and populate dev env."""

    if ENV_NAME not in _list_edm_envs():
        print(f"Creating development environment {ENV_NAME}...")
        cmd = ["edm", "envs", "create", ENV_NAME, "--version", "3.8", "--force"]
        subprocess.run(cmd, check=True)

        cmd = ["edm", "install", "-e", ENV_NAME, "-y"] + EDM_DEPS
        subprocess.run(cmd, check=True)

        cmd = ["edm", "run", "-e", ENV_NAME, "--", "pip", "install"] + PIP_DEPS
        subprocess.run(cmd, check=True)

        print("Bootstrap complete.")

    else:
        print("Environment already exists; reusing.")

    print(f"Activating dev environment {ENV_NAME}")
    subprocess.run(["edm", "shell", "-e", ENV_NAME])


def _list_edm_envs():
    cmd = ["edm", "envs", "list"]
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

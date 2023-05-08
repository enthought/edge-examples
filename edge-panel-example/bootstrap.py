# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Bootstrap file for the edge-hello-world example.
"""

import os
import subprocess

from ci.config import EDM_DEPS, ENV_NAME, PIP_DEPS


CI_EDM_CONFIG = os.environ.get("EDM_CONFIG")
CI_EDM_TOKEN = os.environ.get("EDM_TOKEN")
base_cmd = ["edm"]
if CI_EDM_CONFIG is not None:
    print(f"Discovered edm.yml from CI environment variables {CI_EDM_CONFIG}")
    base_cmd.append("-c")
    base_cmd.append(CI_EDM_CONFIG)
if CI_EDM_TOKEN is not None:
    print("Discovered EDM token from CI environment variable")
    base_cmd.append("-t")
    base_cmd.append(CI_EDM_TOKEN)

def bootstrap():
    """Create and populate dev env"""

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
    print(f'To use your new dev environment, run "edm shell -e {ENV_NAME}"')


if __name__ == "__main__":
    bootstrap()

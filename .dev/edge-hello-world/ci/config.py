import os

APP_NAME = "Edge Hello World"
IMAGE_NAME = "quay.io/enthought/edge-hello-world"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-hello-world"
ENV_NAME = "edge-hello-world"
DEV_CMD = ["flask", "--app", "application/app.py", "run"]

LINT_ENV_NAME = f"lint-{ENV_NAME}"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
CI_DIR = os.path.join(MODULE_DIR, "ci")
SRC_DIR = os.path.join(MODULE_DIR, "src")

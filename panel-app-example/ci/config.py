import os

APP_NAME = "Edge Panel Example"
IMAGE_NAME = "quay.io/enthought/edge-panel-example"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-panel-example"
ENV_NAME = "edge-panel-example"

# Dependencies for bootstrap.py development environment
EDM_DEPS = ["click", "flask>2", "enthought_edge", "pytest", "requests", "panel", "pandas", "matplotlib"]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
]

# Development command for running the application in watch mode
DEV_CMD = ["panel", "serve", "application/app.py", "--port=9000", "--allow-websocket-origin=*"]

LINT_ENV_NAME = f"lint-{ENV_NAME}"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
CI_DIR = os.path.join(MODULE_DIR, "ci")
SRC_DIR = os.path.join(MODULE_DIR, "src")

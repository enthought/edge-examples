import os

APP_NAME = "Edge Flask App"
IMAGE_NAME = "quay.io/enthought/edge-flask-app"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-flask-app"
ENV_NAME = "edge-flask-app"

# Dependencies for bootstrap.py development environment
EDM_DEPS = ["click", "flask>2", "enthought_edge", "pytest", "requests", "opencv_python"]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
    "Flask-Session",
    "supervisor@git+https://github.com/Supervisor/supervisor"
]

# Development command for running the application in watch mode
DEV_CMD = ["python", "./dev/run.py"]

LINT_ENV_NAME = f"lint-{ENV_NAME}"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
CI_DIR = os.path.join(MODULE_DIR, "ci")
SRC_DIR = os.path.join(MODULE_DIR, "src")

import os

APP_NAME = "Edge Streamlit Example"
IMAGE_NAME = "quay.io/enthought/edge-streamlit-example"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-streamlit-example"
ENV_NAME = "edge-streamlit-example"

# Dependencies for bootstrap.py development environment
EDM_DEPS = ["click", "flask>2", "enthought_edge", "pytest", "requests"]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
    "streamlit",
    "streamlit-javascript",
    "streamlit-extras"
]

DEV_CMD = ["streamlit", "run", "application/app.py", "--server.headless", "true", "--server.port", "9000"]



LINT_ENV_NAME = f"lint-{ENV_NAME}"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
CI_DIR = os.path.join(MODULE_DIR, "ci")
SRC_DIR = os.path.join(MODULE_DIR, "src")

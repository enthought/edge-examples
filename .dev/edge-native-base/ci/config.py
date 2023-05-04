import os

APP_NAME = "Edge Native Base"
IMAGE_NAME = "quay.io/enthought/edge-native-base"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-native-base"
ENV_NAME = "edge-native-base"
DEV_CMD = ["edm", "run", "--", "python", "-m", "http.server", "9000", "--directory", "default"]

LINT_ENV_NAME = f"lint-{ENV_NAME}"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
CI_DIR = os.path.join(MODULE_DIR, "ci")
SRC_DIR = os.path.join(MODULE_DIR, "src")

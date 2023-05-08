import os
import subprocess

from .builders import ContainerBuilder, DevBuilder, PreflightBuilder

APP_NAME = "Edge Streamlit Example"
IMAGE_NAME = "quay.io/enthought/edge-streamlit-example"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-streamlit-example"
ENV_NAME = "edge-streamlit-example"

# Dependencies for bootstrap.py development environment
EDM_DEPS = ["click", "enthought_edge", "pytest", "requests"]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
    "streamlit",
    "streamlit-javascript",
    "streamlit-extras",
]

# EDM dependencies that will be packaged into the Docker container
BUNDLE_PACKAGES = [
    "enthought_edge",
    "appdirs",
    "packaging",
    "pip",
    "pyparsing",
    "setuptools",
    "six",
    "requests" 
]



LINT_ENV_NAME = f"lint-{ENV_NAME}"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
CI_DIR = os.path.join(MODULE_DIR, "ci")
SRC_DIR = os.path.join(MODULE_DIR, "src")


class StreamlitDevBuilder(DevBuilder):
    def run(self):
        env = os.environ.copy()
        env.update(self.context.env)
        cmd = [
            "streamlit",
            "run",
            "application/app.py",
            "--server.headless",
            "true",
            "--server.port",
            "9000",
        ]
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)

    def test(self):
        raise NotImplementedError


DEV_BUILDER_CLS = StreamlitDevBuilder
CONTAINER_BUILDER_CLS = ContainerBuilder
PREFLIGHT_BUILDER_CLS = PreflightBuilder

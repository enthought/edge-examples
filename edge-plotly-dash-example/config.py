import os
import subprocess

from ci.builders import ContainerBuilder, DevBuilder, PreflightBuilder

APP_NAME = "Edge Plotly Dash App"
IMAGE_NAME = "quay.io/enthought/edge-plotly-dash-example"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-plotly-dash"
ENV_NAME = "edge-plotly-dash"

# Dependencies for bootstrap.py development environment
EDM_DEPS = [
    "click",
    "enthought_edge",
    "pytest",
    "requests",
    "pandas",
    "flask>2",
    "dash",
]
PIP_DEPS = ["jupyterhub==2.2.2", "sqlalchemy<2", "dockerspawner", "dash", "pandas"]

# EDM dependencies that will be packaged into the Docker container
BUNDLE_PACKAGES = [
    "enthought_edge",
    "appdirs",
    "packaging",
    "pip",
    "pyparsing",
    "setuptools",
    "six",
    "click",
    "requests",
    "gunicorn",
    "pandas",
    "flask>2",
    "dash",
]
BUNDLE_NAME = "app_environment.zbundle"
MODULE_DIR = os.path.join(os.path.dirname(__file__))
CI_DIR = os.path.join(MODULE_DIR, "ci")
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
LINT_ENV_NAME = f"lint-{ENV_NAME}"
SRC_DIR = os.path.join(MODULE_DIR, "src")


class PlotlyDashDevBuilder(DevBuilder):
    def run(self):
        env = os.environ.copy()
        env.update(self.context.env)
        cmd = ["python", "application/app.py"]
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)


DEV_BUILDER_CLS = PlotlyDashDevBuilder
CONTAINER_BUILDER_CLS = ContainerBuilder
PREFLIGHT_BUILDER_CLS = PreflightBuilder

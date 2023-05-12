import os
import subprocess

from ci.builders import ContainerBuilder, DevBuilder, PreflightBuilder

APP_NAME = "Edge Hello World"
IMAGE_NAME = "quay.io/enthought/edge-hello-world"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-hello-world"
ENV_NAME = "edge-hello-world"

# Dependencies for bootstrap.py development environment
EDM_DEPS = ["click", "flask>2", "enthought_edge>=2.6.0", "pytest", "requests"]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
]

# EDM dependencies that will be packaged into the Docker container
BUNDLE_PACKAGES = [
    "enthought_edge>=2.6.0",
    "appdirs",
    "packaging",
    "pip",
    "pyparsing",
    "setuptools",
    "six",
    "click",
    "gunicorn",
    "flask>2",
    "requests",
]

BUNDLE_NAME = "app_environment.zbundle"
MODULE_DIR = os.path.join(os.path.dirname(__file__))
CI_DIR = os.path.join(MODULE_DIR, "ci")
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
LINT_ENV_NAME = f"lint-{ENV_NAME}"
SRC_DIR = os.path.join(MODULE_DIR, "src")


class HelloWorldDevBuilder(DevBuilder):
    def run(self):
        env = os.environ.copy()
        env.update(self.context.env)
        cmd = ["flask", "--app", "application/app.py", "--debug", "run"]
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)


DEV_BUILDER_CLS = HelloWorldDevBuilder
CONTAINER_BUILDER_CLS = ContainerBuilder
PREFLIGHT_BUILDER_CLS = PreflightBuilder

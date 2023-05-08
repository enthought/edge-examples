import os
import subprocess

from .builders import ContainerBuilder, DevBuilder, PreflightBuilder

APP_NAME = "Edge Flask App"
IMAGE_NAME = "quay.io/enthought/edge-dashboard-app"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-dashboard-app"
ENV_NAME = "edge-dashboard-app"

# Dependencies for bootstrap.py development environment
EDM_DEPS = ["click", "flask>2", "enthought_edge", "pytest", "requests"]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
    "Flask-Session",
    "supervisor@git+https://github.com/Supervisor/supervisor",
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
    "click",
    "flask>2",
    "requests"
]


LINT_ENV_NAME = f"lint-{ENV_NAME}"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
CI_DIR = os.path.join(MODULE_DIR, "ci")
SRC_DIR = os.path.join(MODULE_DIR, "src")


def _npm_build(context):
    env = os.environ.copy()
    env.update(context.env)
    cwd = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src", "application", "frontend")
    )
    cmd = ["npm", "install"]
    subprocess.run(cmd, env=env, cwd=cwd, check=True)
    cmd = ["npm", "run", "build"]
    subprocess.run(cmd, env=env, cwd=cwd, check=True)


class DashboardDevBuilder(DevBuilder):
    def run(self):
        env = os.environ.copy()
        env.update(self.context.env)
        cmd = ["python", "./dev/run.py"]
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)

    def test(self):
        _npm_build(self.context)
        super().test()


class DashboardContainerBuilder(ContainerBuilder):
    def build(self):
        _npm_build(self.context)
        cmd = [
            "docker",
            "build",
            "--build-arg",
            f"CI_IMAGE={self.context.image}",
            "-t",
            f"{self.context.image}",
            "-f",
            "Dockerfile",
            self.context.module_dir,
        ]
        env = os.environ.copy()
        env.update(self.context.env)
        subprocess.run(cmd, check=True)


DEV_BUILDER_CLS = DashboardDevBuilder
CONTAINER_BUILDER_CLS = DashboardContainerBuilder
PREFLIGHT_BUILDER_CLS = PreflightBuilder
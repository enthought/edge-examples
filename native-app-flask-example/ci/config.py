import os
import subprocess

from .builders import ContainerBuilder, DevBuilder

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
    "supervisor@git+https://github.com/Supervisor/supervisor",
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


class NativeFlaskDevBuilder(DevBuilder):
    def run(self):
        env = os.environ.copy()
        env.update(self.context.env)
        cmd = ["python", "./dev/run.py"]
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)

    def test(self):
        _npm_build(self.context)
        super().test()


class NativeFlaskContainerBuilder(ContainerBuilder):
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


DEV_BUILDER_CLS = NativeFlaskDevBuilder
CONTAINER_BUILDER_CLS = NativeFlaskContainerBuilder

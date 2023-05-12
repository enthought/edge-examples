import os
import subprocess

from ci.builders import ContainerBuilder, DevBuilder, PreflightBuilder

APP_NAME = "Edge Native Flask App"
IMAGE_NAME = "quay.io/enthought/edge-native-app-flask-demo"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "edge-native-app-flask"
ENV_NAME = "edge-native-app-flask"

# Dependencies for bootstrap.py development environment
EDM_DEPS = [
    "click",
    "flask>2",
    "enthought_edge>=2.6.0",
    "pytest",
    "requests",
    "opencv_python",
]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
    "Flask-Session",
    "supervisor@git+https://github.com/Supervisor/supervisor",
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
    "flask>2",
    "requests",
    "gunicorn",
    "opencv_python",
]
BUNDLE_NAME = "app_environment.zbundle"
MODULE_DIR = os.path.join(os.path.dirname(__file__))
CI_DIR = os.path.join(MODULE_DIR, "ci")
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
LINT_ENV_NAME = f"lint-{ENV_NAME}"
SRC_DIR = os.path.join(MODULE_DIR, "src")


def _npm_build(context):
    env = os.environ.copy()
    env.update(context.env)
    cwd = os.path.abspath(os.path.join(SRC_DIR, "application", "frontend"))
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
    def build(self, *args, **kwargs):
        _npm_build(self.context)
        super().build(*args, **kwargs)


DEV_BUILDER_CLS = NativeFlaskDevBuilder
CONTAINER_BUILDER_CLS = NativeFlaskContainerBuilder
PREFLIGHT_BUILDER_CLS = PreflightBuilder

import os
import subprocess
from .hook import BuilderHook

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
    "opencv_python",
    "flask>2",
    "gunicorn"
]

# Development command for running the application in watch mode
DEV_CMD = ["python", "./dev/run.py"]

LINT_ENV_NAME = f"lint-{ENV_NAME}"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
CI_DIR = os.path.join(MODULE_DIR, "ci")
SRC_DIR = os.path.join(MODULE_DIR, "src")

class NpmHook(BuilderHook):
    def npm_build(self, env):
        cwd = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "src",
                "application",
                "frontend"
            )
        )
        cmd = [
            "npm",
            "install"
        ]
        subprocess.run(cmd, env=env, cwd=cwd, check=True)
        cmd = [
            "npm",
            "run",
            "build"
        ]
        subprocess.run(cmd, env=env, cwd=cwd, check=True)

    def pre(self, env, mode, action):
        action = f"{mode} {action}"
        if action == "dev test" or action == "container build":
            self.npm_build(env)

BUILDER_HOOK = NpmHook()

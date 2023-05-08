import os
import subprocess
from subprocess import Popen


class Builder:
    """A base class for building and running native apps"""

    @property
    def context(self):
        return self._context

    def run(self):
        raise NotImplementedError

    def test(self):
        raise NotImplementedError

    def __init__(self, context):
        """Init function

        Parameters
        ----------
        context : context.BuildContext
            A context with build settings
        """
        self._context = context


class DevBuilder(Builder):
    """A builder class for native apps in dev mode"""

    def __init__(self, *args, **kwargs):
        """Init function

        context : context.DevBuildContext
            A context with development build settings
        """
        super().__init__(*args, **kwargs)

    def run(self):
        env = os.environ.copy()
        env.update(self.context.env)
        cmd = ["python", "-m", "http.server", "9000", "--directory", "default"]
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)

    def test(self):
        cmd = ["pytest", self.context.src_dir]
        env = os.environ.copy()
        env.update(self.context.env)
        env["PYTHONPATH"] = self._context.src_dir
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)


class ContainerBuilder(Builder):
    """A builder class for native apps in container mode"""

    @property
    def _test_path(self):
        return "ci/tests/test_container.py"

    def __init__(self, context):
        """Init function

        context : context.ContainerBuildContext
            A context with container build settings
        """
        super().__init__(context)

    def run(self):
        """Runs the container"""
        env = os.environ.copy()
        env.update(self.context.env)
        self.cleanup()
        self.start()

    def start(self, daemon=False):
        _docker_run(
            self.context.image, self.context.container_name, self.context.env, daemon
        )

    def cleanup(self):
        _docker_stop(self.context.container_name)
        _docker_remove(self.context.container_name)

    def build(self):
        """Build the application's docker image"""
        cmd = [
            "docker",
            "build",
            "-t",
            f"{self.context.image}",
            "-f",
            "Dockerfile",
            self.context.module_dir,
        ]
        env = os.environ.copy()
        env.update(self.context.env)
        subprocess.run(cmd, check=True)

    def test(self, verbose=False):
        """Test the application container"""
        cmd = ["pytest"]
        if verbose:
            cmd.append("-vvvs")
        cmd.append(self._test_path)
        env = os.environ.copy()
        env["PYTHONPATH"] = self.context.module_dir
        if self.context.edge_settings_file is not None:
            env["EDGE_SETTINGS_FILE"] = self.context.edge_settings_file
        subprocess.run(cmd, check=True, env=env, cwd=self.context.module_dir)

    def publish(self):
        """Publishes the application's docker image"""
        cmd = ["docker", "push", f"{self.context.image}"]
        env = os.environ.copy()
        subprocess.run(cmd, env=env, check=True)


class PreflightBuilder(ContainerBuilder):
    """A builder class for native apps in preflight mode"""

    @property
    def _test_path(self):
        return "ci/tests/test_preflight.py"

    def __init__(self, context):
        """Init function

        context : context.PreflightBuildContext
            A context with preflight settings
        """
        super().__init__(context)

    def publish(self):
        raise NotImplementedError

    def build(self):
        raise NotImplementedError

    def run(self):
        """Start the application"""
        process = self.start_jupyterhub()
        process.wait()

    def test(self, verbose=False):
        """Test the application container"""
        cmd = ["pytest"]
        if verbose:
            cmd.append("-vvvs")
        cmd.append(self._test_path)
        env = os.environ.copy()
        env["PYTHONPATH"] = self.context.module_dir
        if self.context.edge_settings_file is not None:
            env["EDGE_SETTINGS_FILE"] = self.context.edge_settings_file
        subprocess.run(cmd, check=True, env=env, cwd=self.context.module_dir)

    def start_jupyterhub(self):
        self.cleanup()
        cmd = ["jupyterhub", "-f", "ci/jupyterhub_config.py"]
        env = os.environ.copy()
        env.update(self.context.env)
        process = Popen(cmd, env=env)
        return process


def _docker_stop(container_name):
    """Stops a docker container

    Parameters
    ----------
    container_name : str
        The name of the container to stop
    """
    env = os.environ.copy()
    remove_container_cmd = ["docker", "stop", container_name]
    subprocess.run(remove_container_cmd, env=env)


def _docker_remove(container_name):
    """Removes any existing containers from container mode

    Parameters
    ----------
    container_name : str
        The name of the container to remove
    """
    env = os.environ.copy()
    remove_container_cmd = ["docker", "container", "rm", container_name]
    subprocess.run(remove_container_cmd, env=env)


def _docker_run(image, container_name, container_env={}, daemon=False):
    """Starts the native app in container mode

    Parameters
    ----------
    image : str
        The name of the docker image to start
    container_name : str
        The name of the docker container
    container_env : dict
        A dictionary of extra environment variables to pass to the container
    daemon : boolean
        Whether or not to run the container in Docker daemon mode
    """
    env = os.environ.copy()
    container_env_strings = [f"{k}={v}" for k, v in container_env.items()]
    cmd = ["docker", "run", "-p", "8888:8888", "--name", container_name]
    if daemon:
        cmd.append("-d")
    for container_env in container_env_strings:
        cmd.append("--env")
        cmd.append(container_env)
    cmd.append(image)
    subprocess.run(cmd, check=True, env=env)

import os
import subprocess
from .config import IMAGE_NAME, IMAGE_TAG, CONTAINER_NAME

class Builder:
    """A base class for building and running native apps"""
    @property
    def context(self):
        return self._context

    def run(self):
        raise NotImplemented
  
    def test(self):
        raise NotImplemented
    
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
    def run(self):
        cmd = ["flask", "--app", "application/app.py", "run"]
        env = os.environ.copy()
        env.update(self.context.env)
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)

    def test(self):
        cmd = ["pytest", self.context.src_dir]
        env = os.environ.copy()
        env.update(self.context.env)
        env["PYTHONPATH"] = self._context.src_dir
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)


class ContainerBuilder(Builder):
    """A builder class for native apps in container mode"""
        
    def __init__(self, context):
        """Init function
        
        context : context.ContainerBuildContext
            A context with container build settings
        """
        super().__init__(context)

    def run(self):
        """Runs the container"""
        self.stop_container()
        self.remove_container()
        self.start_container()

    def build(self):    
        """Build the application's docker image"""
        cmd = [
            "docker",
            "build",
            "-t",
            f"{self.context.image}",
            "-f",
            "Dockerfile",
            self.context.module_dir
        ]
        subprocess.run(cmd, check=True)
    
    def test(self):
        """Test the application container"""
        cmd = [
            "pytest",
            "ci/tests/test_container.py"
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = self.context.module_dir
        if self.context.edge_settings_file is not None:
            env["EDGE_SETTINGS_FILE"] = self.context.edge_settings_file
        subprocess.run(cmd, check=True, env=env, cwd=self.context.module_dir)

    def publish(self):
        """Publishes the application's docker image"""
        cmd = ["docker", "push", f"{self.context.image}"]
        subprocess.run(cmd, check=True)

    def stop_container(self):
        """Stops the application container"""
        env = os.environ.copy()
        remove_container_cmd = [
            "docker",
            "stop",
            self.context.container_name
        ]
        subprocess.run(remove_container_cmd, env=env)

    def remove_container(self):
        """Removes any existing containers from container mode
        
        Parameters
        ----------
        context : context.ContainerBuildContext
        """
        env = os.environ.copy()
        remove_container_cmd = [
            "docker",
            "container",
            "rm",
            self.context.container_name
        ]
        subprocess.run(remove_container_cmd, env=env)

    def start_container(self, daemon=False):
        """Starts the native app in container mode
        
        Parameters
        ----------
        context : context.ContainerBuildContext
            The context containing container settings
        daemon : boolean
            Whether or not to run the container in Docker daemon mode
        """
        env = os.environ.copy()
        container_envs = [f"{key}={value}" for key, value in self.context.env.items()]
        cmd = [
            "docker",
            "run",
            "-p",
            "8888:8888",
            "--name",
            self.context.container_name
        ]
        if daemon:
            cmd.append("-d")
        for container_env in container_envs:
            cmd.append("--env")
            cmd.append(container_env)
        cmd.append(f"{self.context.image}")
        subprocess.run(cmd, check=True, env=env)        
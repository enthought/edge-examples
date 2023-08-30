import json
import os

from config import (
    APP_NAME,
    ARTIFACT_DIR,
    BUNDLE_NAME,
    BUNDLE_PACKAGES,
    CI_DIR,
    CONTAINER_NAME,
    IMAGE_NAME,
    IMAGE_TAG,
    MODULE_DIR,
    SRC_DIR,
)


class BuildContext:
    """A class for containing build options for a native app"""

    @property
    def env(self):
        _env = self._get_edge_settings(self.edge_settings_file)
        if self.mode is not None:
            _env["NATIVE_APP_MODE"] = self.mode
            if self.mode in ("container", "dev"):
                _env["EDGE_DISABLE_AUTH"] = "1"
        return _env

    @property
    def app_name(self):
        return self._app_name

    @property
    def src_dir(self):
        return self._src_dir

    @property
    def module_dir(self):
        return self._module_dir

    @property
    def ci_dir(self):
        return self._ci_dir

    @property
    def edge_settings_file(self):
        return self._edge_settings_file

    @property
    def mode(self):
        return None

    def __init__(
        self,
        edge_settings_file=None,
        app_name=APP_NAME,
        src_dir=SRC_DIR,
        module_dir=MODULE_DIR,
        ci_dir=CI_DIR,
    ):
        """Init function

        Parameters
        ----------
        edge_settings_file : str or None
            A path to an edge settings json file
        app_name : str
            The app name
        src_dir : str
            The path of the src directory for the application files
        module_dir : str
            The path of the application module directory
        ci_dir : str
            The path of the CI tools
        """
        self._edge_settings_file = edge_settings_file
        self._app_name = app_name
        self._src_dir = src_dir
        self._module_dir = module_dir
        self._ci_dir = ci_dir

    def _get_edge_settings(self, filename):
        """Retrieve Edge environment variable settings from a file

        Parameters
        ----------
        filename : str or None
            The filename of a json file containing EDGE_API_SERVICE_URL,
            EDGE_API_ORG and EDGE_API_TOKEN

        Returns
        -------
        dict
            If filename is None, an empty dictionary is returned. Otherwise
            a dictionary representing the contents of the json file
            is returned

        Raises
        ------
        ValueError
            Raised if the json file does not contain all required environment
            variables
        """
        if filename is None:
            return {}
        try:
            with open(filename, "r") as f:
                settings = json.load(f)
            for key in ["EDGE_API_SERVICE_URL", "EDGE_API_ORG", "EDGE_API_TOKEN"]:
                if key not in settings:
                    raise ValueError(f"{key} not in settings file")
            return settings
        except FileNotFoundError:
            print(
                f"Could not find optional settings file {filename}; "
                "proceeding without it."
            )
            return {}


class DevBuildContext(BuildContext):
    @property
    def mode(self):
        return "dev"


class ContainerBuildContext(BuildContext):
    """A class for containing container build options for a native app"""

    @property
    def mode(self):
        return "container"

    @property
    def image_name(self):
        return self._image_name

    @property
    def image_tag(self):
        return self._image_tag

    @property
    def image(self):
        return f"{self.image_name}:{self.image_tag}"

    @property
    def container_name(self):
        return self._container_name

    @property
    def bundle_packages(self):
        return self._bundle_packages

    @property
    def bundle_name(self):
        return self._bundle_name

    @property
    def bundle_path(self):
        return os.path.join(self.artifact_dir, self.bundle_name)

    @property
    def artifact_dir(self):
        return self._artifact_dir

    def __init__(
        self,
        *args,
        image_name=IMAGE_NAME,
        image_tag=IMAGE_TAG,
        container_name=CONTAINER_NAME,
        bundle_packages=BUNDLE_PACKAGES,
        bundle_name=BUNDLE_NAME,
        artifact_dir=ARTIFACT_DIR,
        **kwargs,
    ):
        """Init function

        image_name : str
            The docker image name to build
        image_tag : str
            The docker image tag to build
        container_name : str
            The name of the docker container when running in container mode
        bundle_packages : List[str]
            A list of packages to include in the bundle for this container

        Raises
        ------
        ValueError
            Raised if the image_tag value is "latest"
        """
        super().__init__(*args, **kwargs)
        self._image_name = image_name
        if image_tag == "latest":
            raise ValueError("Image tag cannot be latest")
        self._image_tag = image_tag
        self._container_name = container_name
        self._bundle_packages = bundle_packages
        self._bundle_name = bundle_name
        self._artifact_dir = artifact_dir


class PreflightBuildContext(ContainerBuildContext):
    """A class for containing preflight build options for a native app"""

    @property
    def mode(self):
        return None

    @property
    def container_name(self):
        return f"jupyterhub-{self._container_name}"

    @property
    def env(self):
        result = super().env
        result["IMAGE"] = self.image
        result["CONTAINER_NAME"] = self.container_name
        return result

    def __init__(
        self,
        *args,
        image_name=IMAGE_NAME,
        image_tag=IMAGE_TAG,
        container_name=CONTAINER_NAME,
        **kwargs,
    ):
        """Init function

        image_name : str
            The docker image name to build
        image_tag : str
            The docker image tag to build
        container_name : str
            The name of the docker container when running in container mode

        Raises
        ------
        ValueError
            Raised if the image_tag value is "latest"
        """
        super().__init__(*args, **kwargs)
        self._image_name = image_name
        if image_tag == "latest":
            raise ValueError("Image tag cannot be latest")
        self._image_tag = image_tag
        self._container_name = container_name

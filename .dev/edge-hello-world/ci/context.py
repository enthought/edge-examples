import json
from .config import APP_NAME, IMAGE_NAME, IMAGE_TAG, CONTAINER_NAME

class BuildContext:
    """A class for containing build options for a native app"""
    @property
    def env(self):
        return self._env

    @property
    def app_name(self):
        return self._app_name
    
    def __init__(
        self,
        edge_settings_file=None,
        mode=None,
        app_name=APP_NAME,

    ):
        """Init function
        
        Parameters
        ----------
        edge_settings_file : str or None
            A path to an edge settings json file
        mode : str or None
            The development mode dev, container or preflight
        app_name : str
            The app name
        """
        self._env = self._get_edge_settings(edge_settings_file)
        if mode is not None:
            self._env["NATIVE_APP_MODE"] = mode
        self._app_name = app_name

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
        with open(filename, "r") as f:
            settings = json.load(f)
        for key in ["EDGE_API_SERVICE_URL", "EDGE_API_ORG", "EDGE_API_TOKEN"]:
            if key not in settings:
                raise ValueError(f"{key} not in settings file")
        return settings

class ContainerBuildContext(BuildContext):
    """A class for containing container build options for a native app"""
    @property
    def image_name(self):
        return self._image_name

    @property
    def image_tag(self):
        return self._image_tag

    @property
    def container_name(self):
        return self._container_name
        
    def __init__(
        self,
        *args,
        image_name=IMAGE_NAME,
        image_tag=IMAGE_TAG,
        container_name=CONTAINER_NAME,
        **kwargs
    ):
        """Init function
        
        image_name : str
            The docker image name to build
        image_tag : str
            The docker image tag to build
        container_name : str
            The name of the docker container when running in container mode
        """
        super().__init__(*args, **kwargs)
        self._image_name = image_name
        if image_tag == "latest":
            raise ValueError("Image tag cannot be latest")
        self._image_tag = image_tag
        self._container_name = container_name        
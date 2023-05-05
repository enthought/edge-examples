class BuilderHook:
    """A class that allows pre-build actions to occur"""
    def pre(self, env, mode, action):
        """
        Run during CI prior to each Builder command

        Parameters
        ----------
        env : dict
            An environment dictionary that will be used with
            the builder command
        mode : str
            The name of the CI mode being used:
            "dev", "container", "preflight"
        action : str
            The name of the CI action being used:
            "build", "run", "test", "publish"
        """
        pass
    
    def post(self, env, mode, action):
        """
        Run during CI after each Builder command

        Parameters
        ----------
        env : dict
            An environment dictionary that will be used with
            the builder command
        mode : str
            The name of the CI mode being used:
            "dev", "container", "preflight"
        action : str
            The name of the CI action being used:
            "build", "run", "test", "publish"
        """
        pass

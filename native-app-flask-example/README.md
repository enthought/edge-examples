# Native App Example

This folder contains a Flask + React application that showcases how to
create an Edge native application. The native app is packaged as a docker image that will be consumed by the Edge's JupyterHub spawner system.

## Requirements

To build and run the example application you will need:
- [Docker](https://docke.com)
- [Node JS}(https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

## Set up the development environment

First, you will need to create an EDM environment named `dev_env` and install some dependencies.

```commandline
edm install -e dev_env --version 3.8 -y click requests opencv_python "flask>2" && \
edm run -e dev_env -- python -m pip install "jupyterhub==2.2.2" \
    dockerspawner \
    "configurable-http-proxy" \
    Flask-Session
```   

Once you have created the `dev_env` environment, you may activate it with:

```commandline
edm shell -e dev_env
```   

## Running the Application

If you are running the application for the first time, you will need to build
the application's Docker image. From within the `native-app-flask-example` directory
run:

```commandline
    python -m ci build
```

Once built, you can run the image from a local JupyterHub session by running:

```commandline
    python -m ci start
```

For your local JupyterHub session, your username is `dummy` and the password is `password`.

## Local Development

For development purposes, you may run this application outside of a JupyterHub using file
watch modes for automatic reloading. To start the application and watch backend changes:

```commandline
    python -m ci watch backend
```
To watch the frontend changes:

```commandline
    python -m ci watch frontend
```


## Requirements for a Edge native application

Edge's JupyterHub spawner will launch a native application's container and provide
environment variables for routing and authentication.

### Using port and URL prefix provided by `JupyterHub`: 

Once the native application is spawned, the environment variable `JUPYTERHUB_SERVICE_URL`
will be available. Users need to set the listening port and URL prefix of the
application with values extracted from this variable. A `wsgi` based application such as
Flask should bind to the hostname and port specified in this variable.

```python
# native-app-flask-example/wsgi.py
    ...
    service_url = os.environ.get('JUPYTERHUB_SERVICE_URL', None)
    port = 8888
    host = '0.0.0.0'
    if service_url:
        url = urlparse(service_url)
        port = url.port
        host = url.hostname
    options = {
        'bind': f'{host}:{port}',
        'workers': 1,
    }
    application = create_app()
    StandaloneApplication(application, options).run()
```

### Reporting server activities back to Edge: 

Edge will shut your application down after a while if it is considered inactive.
To avoid this, you will need to report activity back to the server when the user
interacts with your app. 

To report activities, users can send a POST to the URL provided in the
`JUPYTERHUB_ACTIVITY_URL` environment variable, using the token provided
in `JUPYTERHUB_API_TOKEN`. In this native app example, the 
[`trackactivity` decorator](./src/app.py#L61) is used to perform this POST
whenever any Flask endpoint is accessed.

## The authentication flow using JupyterHub as an OAuth provider

Since the `jupyterHub` only proxies connections to the single-user server,
it's the job of the server (`Flask` in this case) to provide the user authentication
service. To simplify the process, `JupyterHub` can act as an OAuth provider for the
single-user server.
The authentication flow generally goes like this:

* Create the `JupyterHub` authenticator (`jupyterhub.services.auth.HubOAuth`)
with the `JUPYTERHUB_API_TOKEN` environment variable. This object provides methods
to generate user's tokens, identify the user from tokens...

    ```python
    ...
    API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", "")
    AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60)
    ```
* A non-authenticated user makes a request to access your application, the server
redirects the user to the "authorize" endpoint on `JupyterHub` with extra information:
    - the *state* of the request, given the redirect target.
    - the cookie name for storing OAuth state.

    ```python
        ...
        else:
            # redirect to login url on failed auth
            state = AUTH.generate_state(next_url=request.path)
            response = make_response(redirect(AUTH.login_url + "&state=%s" % state))
            response.set_cookie(AUTH.state_cookie_name, state)
            return response
    ```
* After the user is authenticated with `JupyterHub`, the browser is redirected to the
OAuth callback handle of the `Flask` server with the OAuth code. Your application needs
to have this handle implemented to generate the user's token from this code.

```python
    @app.route(PREFIX + "oauth_callback")
    def oauth_callback():
        code = request.args.get("code", None)
        if code is None:
            return "Forbidden", 403

        arg_state = request.args.get("state", None)
        cookie_state = request.cookies.get(AUTH.state_cookie_name)
        if arg_state is None or arg_state != cookie_state:
            return "Forbidden", 403

        session["token"] = AUTH.token_for_code(code)

        next_url = AUTH.get_next_url(cookie_state) or PREFIX
        response = make_response(redirect(next_url))
        return response
```

* Finally, the authenticated user is redirected back to the original URL. 




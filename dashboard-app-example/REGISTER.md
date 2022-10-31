# Registering this Application

After the image for this application has been published using `python -m ci publish`,
an application tile can be created on Edge. You will need:

- The `enthought_edge` package from the `enthought/edge` EDM repository
- A quay.io deployment credential for the `quay.io/enthought/edge-dashboard-demo:latest` repo
- Development access for an Edge organization
- An Edge API token

You can use the following Python code to register the application:

```
from edge.api import EdgeSession
from edge.apps.application import Application
from edge.apps.app_version import AppKindEnum, AppVersion
from edge.apps.server_info import ServerInfo

# Create an Edge session
edge = EdgeSession(
    service_url="https://edge-dev-main.platform-devops.enthought.com/services/api",
    version_num=1,
    organization="<YOUR_ORGANIZATION>",
    api_token="<YOUR_API_TOKEN>"
)

# Register a new application
app = Application('nativeapp', True)
edge.applications.add_application(app)

# Register server info
server = ServerInfo(
    'nativeapp',
    'quay.io',
    '<QUAY_USERNAME>',
    '<QUAY_PASSWORD>'
)
edge.applications.add_server_info(server)

# Register the application version
ICON = (
    "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/w"
    "D/AP+gvaeTAAABfklEQVRoge2ZTU7DMBBGHz9bECpLWAI36ZIdEvQa5Rpw"
    "CFQhtaq66o5wErgCWSR7KAvbUrGaFI8Tu5XmSZbjuFK/mS/jNjYoiqLsMp"
    "fAHKiBVeJWAwvgOkZ8mUG430rgQhLAfAfEuzZrEnnQEkANnAQG3RcVcLZp"
    "oi2AlTe+7UzO/1h6441aDxMI6ZUcASz5m11/HMTeO3Cc8Lv8LDeNg2pNHQ"
    "jAZdbPtCjzDnUgAK2BTWgN5CalAw4/01H/sfbeAQ0gN5IaOAJGwNBeF8AE"
    "+LHzna4y25AEMALu18Z3GPGTThQFIglgaPsx8NmhFhGSGhjYPrt4iPsdeM"
    "G8NxfAFPj25sVvWSHErEID4Bx4sM3xEaUokBgHxpgEPGHq4tXef/Q+16sT"
    "EgdK269vc/hbMMmQOFBgHpln714WJAFMbe+W0zdatv76RnfmctPmQAWcph"
    "KyhcbN3TYH3vvRIkK0SNwAX+Q/GyiBK0kAYE5GZhgLUwuvMIcsYvGKoij9"
    "8ws479akcYBsnQAAAABJRU5ErkJggg=="
)
version1 = AppVersion(
    app.app_id,
    "1",
    "Edge Dashboard App Demo, v1",
    "Demonstration of a dashboard application",
    ICON,
    AppKindEnum.Native,
    "quay.io/enthought/edge-dashboard-demo:latest",
    "edge.dashboard"
)
edge.applications.add_app_version(version1)
```
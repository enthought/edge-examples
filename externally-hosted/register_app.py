# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

from edge.apps.app_version import AppKindEnum, AppVersion
from edge.apps.application import Application, AppResource

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


app = Application(
    app_id="external-demo",
    visible_versions=[],
    visible_auto_add=True,
    max_resources=AppResource(cpu=1, gpu=0, memory=1000000),
    max_global_resources=AppResource(cpu=10, gpu=1, memory=20000000),
)


version1 = AppVersion(
    app_id=app.app_id,
    version="1.0.0",
    title="Version #1",
    description="First version, setting a baseline",
    icon=ICON,
    kind=AppKindEnum.External,
    link="https://edge-dev.platform-devops.enthought.com",
    profiles={
        "small": AppResource(cpu=1, gpu=0, memory=1000000, shutdown=7200),
        "less-small": AppResource(cpu=2, gpu=0, memory=2000000, shutdown=14400),
    },
    default_profile="small",
    volume_mount_point="/data",
    suggested_volume_size=1,
)


def register_app(session):
    """Add the demo app with Edge, and register it as an OAuth2 client"""
    session.applications.add_application(app)
    session.applications.add_app_version(version1)

    return session.applications.register_oauth_client(
        app.app_id, "http://edge-dev.platform-devops.enthought.com/authorize"
    )

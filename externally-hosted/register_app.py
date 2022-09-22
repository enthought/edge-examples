# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import base64

from edge.apps.app_version import AppKindEnum, AppVersion
from edge.apps.application import Application, AppResource

# Icon must be base64-encoded
with open('icon.png','rb') as f:
    icon = base64.b64encode(f.read())

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
    description="Demo for externally-hosted applications",
    icon=icon,
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

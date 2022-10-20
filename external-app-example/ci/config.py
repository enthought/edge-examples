# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.
"""
Configuration and Settings for the ci module
"""
import os
import socket

EXTERNAL_EXAMPLE_IMAGE = "quay.io/enthought/edge-external-app-demo"

def discover_ip():
    """Find the IP address we are connected to. More or less does the
    same thing as get_external_ip() but not using the SDK."""
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(("10.255.255.255", 1))
        ip = st.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        st.close()
    return ip

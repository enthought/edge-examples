# Enthought product code
#
# (C) Copyright 2010-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Example Flask application (external).
"""

import os
from flask import Flask, render_template_string, request

PREFIX = os.environ.get("PREFIX", "/")

app = Flask(__name__)

@app.get(PREFIX)
def root():
    headers = dict(request.headers)
    
    html = """
    <html>
    <head>
        <title>External Example Flask application</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            th { background-color: #4CAF50; color: white; }
        </style>
    </head>
    <body>
        <h1>Hello {{ headers.get('X-Forwarded-Display-Name', 'Unknown') }}!</h1>
        <h2>Request Headers</h2>
        <table>
            <tr>
                <th>Header</th>
                <th>Value</th>
            </tr>
            {% for header, value in headers.items() %}
            <tr>
                <td style="white-space: nowrap;">{{ header }}</td>
                <td style="word-break: break-all; word-wrap: break-word;">{{ value }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    
    return render_template_string(html, headers=headers)

# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import base64
import os

import cv2
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))
face_cascade = cv2.CascadeClassifier(
    os.path.join(dir_path, "haarcascade_frontalface_default.xml")
)


def detect_face(encoded_data: str, params: dict) -> str:

    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    scaleFactor = params.get("scaleFactor", 1.1)
    minNeighbors = params.get("minNeighbors", 4)
    faces = face_cascade.detectMultiScale(gray, scaleFactor, int(minNeighbors))
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    _, buffer = cv2.imencode(".jpeg", img)
    return base64.b64encode(buffer).decode("utf-8")

#!/usr/bin/env python3
"""
 This was originally pilfered from
 https://github.com/adeept/Adeept_RaspTank/blob/a6c45e8cc7df620ad8977845eda2b839647d5a83/server/app.py

 Which looks like it was in turn pilfered from
 https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited

"""

import os
import threading
import requests
import logging
from requests_toolbelt.multipart.encoder import MultipartEncoder

from flask import Flask, Response, request, send_from_directory

# from flask.logging import logging as flask_logging
from flask_cors import CORS

import cv2

import constants
import web_utils
import log
import rotobot_api

from base_camera import BaseCamera
from camera_opencv import OpenCvCamera, VIDEO_OUTPUT_FILE_TRIMMED


app = Flask(__name__)
CORS(app, supports_credentials=True)


class LogFilter(logging.Filter):
    def filter(self, record):
        return "GET /ping" not in record.getMessage()


# werkzeug is the filter used by flask
logging.getLogger("werkzeug").addFilter(LogFilter())

camera = OpenCvCamera()


def gen_rgb_video(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()

        jpeg = cv2.imencode(".jpg", frame)[1].tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")


@app.route("/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        gen_rgb_video(camera), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route("/capture")
def capture():
    """Capture a photo and upload it to twerk api/photoUpload"""
    productId = request.args.get("productId")
    if productId is None:
        return web_utils.respond_not_ok(app, "missing required param", "productId")

    frame = camera.get_frame()
    cv2.imwrite("capture.jpg", frame)

    mp_encoder = MultipartEncoder(
        fields={
            # plain file object, no filename or mime type produces a
            # Content-Disposition header with just the part name
            "productId": productId,
            "files": ("capture.jpg", open("capture.jpg", "rb"), "image/jpg"),
        }
    )

    log.info(f"uploading capture to {constants.TWERK_PHOTO_UPLOAD_URL}")
    response = requests.post(
        constants.TWERK_PHOTO_UPLOAD_URL,
        data=mp_encoder,
        headers={
            "Content-Type": mp_encoder.content_type,
        },
    )
    respJson = response.json()
    log.info(f"capture response: {respJson}")
    return web_utils.json_response(app, response.json())


@app.route("/capture_turntable")
def capture_turntable_video():
    productId = request.args.get("productId")
    if productId is None:
        return web_utils.respond_not_ok(app, "missing required param", "productId")

    rotobot_api.rotate_360()
    camera.capture_video()

    log.info("invoking Multipart encoder")
    mp_encoder = MultipartEncoder(
        fields={
            # plain file object, no filename or mime type produces a
            # Content-Disposition header with just the part name
            "productId": productId,
            "files": (
                VIDEO_OUTPUT_FILE_TRIMMED,
                open(VIDEO_OUTPUT_FILE_TRIMMED, "rb"),
                "video/mp4",
            ),
        }
    )

    log.info(f"uploading capture to {constants.TWERK_PHOTO_UPLOAD_URL}")
    response = requests.post(
        constants.TWERK_PHOTO_UPLOAD_URL,
        data=mp_encoder,
        headers={
            "Content-Type": mp_encoder.content_type,
        },
    )
    respJson = response.json()
    log.info(f"capture response: {respJson}")
    return web_utils.json_response(app, response.json())


@app.route("/stats")
def send_stats():
    (cpu_temp, *rest) = [
        int(i) / 1000
        for i in os.popen("cat /sys/devices/virtual/thermal/thermal_zone*/temp")
        .read()
        .split()
    ]
    return web_utils.json_response(
        app,
        {
            "cpu_temp": cpu_temp,
            "capture": BaseCamera.stats(),
        },
    )


@app.route("/ping")
def ping():
    return web_utils.respond_ok(app, "pong")


@app.route("/<path:filename>")
def send_file(filename):
    return send_from_directory(dir_path, filename)


@app.route("/")
def index():
    return send_from_directory(dir_path, "index.html")


class webapp:
    def __init__(self):
        self.camera = camera

    def thread(self):
        app.run(host="0.0.0.0", port=constants.SERVER_PORT, threaded=True)

    def start_thread(self):
        thread = threading.Thread(target=self.thread)
        thread.setDaemon(False)
        thread.start()  #


log.info("photo-bot server starting...")

flask_app = webapp()
flask_app.start_thread()

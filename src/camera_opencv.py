"""
 This was originally pilfered from
 https://github.com/adeept/Adeept_RaspTank/blob/a6c45e8cc7df620ad8977845eda2b839647d5a83/server/camera_opencv.py

 Which looks like it was in turn pilfered from
 https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited

"Great artists steal". Thank you, @adeept and @miguelgrinberg!
"""
import os
import cv2

from base_camera import BaseCamera
import constants as c
import log


class OpenCvCamera(BaseCamera):
    video_source = 0
    img_is_none_messaged = False

    def __init__(self):
        OpenCvCamera.set_video_source(c.CAMERA_CHANNEL)
        super(OpenCvCamera, self).__init__()

    @staticmethod
    def set_video_source(source):
        log.info(f"setting video source to {source}")
        OpenCvCamera.video_source = source

    @staticmethod
    def frames():
        log.info("initializing VideoCapture ")

        camera = cv2.VideoCapture(
            OpenCvCamera.video_source
        )  # , apiPreference=cv2.CAP_V4L2)
        if not camera.isOpened():
            raise RuntimeError("Could not start camera.")

        log.info(f"setting camera resolution to {c.CAMERA_WIDTH}x{c.CAMERA_HEIGHT}")
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, c.CAMERA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, c.CAMERA_HEIGHT)

        # Doing the rotation using cv2.rotate() was a 6-7 FPS drop
        # Unfortunately, you can't set the rotation on the v4l driver
        # on raspian bullseye before doing the opencv init above - why, idk.
        log.info(f"setting camera rotation to {c.CAMERA_ROTATION}")
        os.system(f"sudo v4l2-ctl --set-ctrl=rotate={c.CAMERA_ROTATION}")

        log.info("starting read loop")
        while True:
            _, img = camera.read()
            # log.info("read image")
            if img is None:
                if not OpenCvCamera.img_is_none_messaged:
                    log.error(
                        "The camera has not read data, please check whether the camera can be used normally."
                    )
                    log.error(
                        "Use the command: 'raspistill -t 1000 -o image.jpg' to check whether the camera can be used correctly."
                    )
                    OpenCvCamera.img_is_none_messaged = True
                continue

            yield img

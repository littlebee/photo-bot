"""
 This was originally pilfered from
 https://github.com/adeept/Adeept_RaspTank/blob/a6c45e8cc7df620ad8977845eda2b839647d5a83/server/camera_opencv.py

 Which looks like it was in turn pilfered from
 https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited

"Great artists steal". Thank you, @adeept and @miguelgrinberg!
"""
import os
import subprocess
import cv2
import time

from base_camera import BaseCamera, CameraEvent

import constants as c
import log

VIDEO_DURATION = 7  # seconds
VIDEO_OUTPUT_FILE = "videoCapture.mp4"
VIDEO_OUTPUT_FILE_TRIMMED = "videoCaptureTrimmed.mp4"


class OpenCvCamera(BaseCamera):
    video_source = 0
    is_capturing = False
    img_is_none_messaged = False
    video_ready = CameraEvent()
    video_capture_error = None

    def __init__(self):
        OpenCvCamera.set_video_source(c.CAMERA_CHANNEL)
        super(OpenCvCamera, self).__init__()

    @staticmethod
    def set_video_source(source):
        log.info(f"setting video source to {source}")
        OpenCvCamera.video_source = source

    @staticmethod
    def capture_video():
        """
        This function is called from the main thread to start the video capture
        """
        log.info("starting video capture")
        OpenCvCamera.is_capturing = True
        OpenCvCamera.video_ready.wait()
        OpenCvCamera.video_ready.clear()
        if OpenCvCamera.video_capture_error is not None:
            raise RuntimeError(OpenCvCamera.video_capture_error)
            OpenCvCamera.video_capture_error = None

    @staticmethod
    def frames():
        camera = OpenCvCamera.setup_camera()
        log.info("starting read loop")
        img = None
        while True:
            if OpenCvCamera.is_capturing:
                # OpenCvCamera._capture_cv2_video(camera)

                camera.release()
                OpenCvCamera._capture_raspi_video()
                camera = OpenCvCamera.setup_camera()

                OpenCvCamera.is_capturing = False
                OpenCvCamera.video_ready.set()
                # yields the last frame before the video capture to allow
                # the BaseCamera frames loop to continue
                yield img
            else:
                _, img = camera.read()
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

    @staticmethod
    def setup_camera():
        log.info("initializing VideoCapture ")

        camera = cv2.VideoCapture(
            OpenCvCamera.video_source
        )  # , apiPreference=cv2.CAP_V4L2)
        if not camera.isOpened():
            raise RuntimeError("Could not start camera.")

        log.info(
            f"setting camera resolution to {c.CAMERA_WIDTH}x{c.CAMERA_HEIGHT}@{c.CAMERA_FPS}fps"
        )
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, c.CAMERA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, c.CAMERA_HEIGHT)
        camera.set(cv2.CAP_PROP_FPS, c.CAMERA_FPS)
        # camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("M", "J", "P", "G"))

        log.info(f"setting camera auto exposure to {c.CAMERA_AUTO_EXPOSURE}")
        camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, c.CAMERA_AUTO_EXPOSURE)

        # removes flicker from 60hz lights
        log.info("setting camera power_line_frequency")
        os.system("v4l2-ctl --set-ctrl power_line_frequency=2")

        # set white balance to 3200k
        log.info("setting camera white balance")
        os.system(
            "v4l2-ctl --set-ctrl white_balance_auto_preset=0,red_balance=2600,blue_balance=2100"
        )

        # Doing the rotation using cv2.rotate() was a 6-7 FPS drop
        # Unfortunately, you can't set the rotation on the v4l driver
        # on raspian bullseye before doing the opencv init above - why, idk.
        log.info(f"setting camera rotation to {c.CAMERA_ROTATION}")
        os.system(f"sudo v4l2-ctl --set-ctrl=rotate={c.CAMERA_ROTATION}")

        return camera

    @staticmethod
    def _capture_cv2_video(camera):
        log.info("capturing video")

        start = time.time()
        num_frames = 0
        captured_frames = []
        while True:
            ret, frame = camera.read()

            if ret is True:
                captured_frames.append(frame)
                num_frames += 1

            # Break the loop
            else:
                print(f"Error capturing image {ret}")
                break

            if time.time() - start >= VIDEO_DURATION:
                break

        actual_duration = time.time() - start
        actual_fps = num_frames / actual_duration
        print(
            f"recorded {num_frames} frames in {actual_duration}s ({actual_fps:.2f} fps)"
        )

        print(f"\nSaving video to {VIDEO_OUTPUT_FILE}")

        writer = cv2.VideoWriter(
            VIDEO_OUTPUT_FILE,
            cv2.VideoWriter_fourcc(*"mp4v"),
            actual_fps,
            (c.CAMERA_WIDTH, c.CAMERA_HEIGHT),
        )
        for frame in captured_frames:
            writer.write(frame)

    @staticmethod
    def _capture_raspi_video():
        raspi_cmd = "raspivid -o -  -t 7000 -ex night -br 50 -w 1920 -h 1080 -fps 30"
        # ffmpeg -r 20 -i - -y -vcodec copy videoCapture.mp4
        ffmpeg_cmd = f"ffmpeg -r 20 -i - -y -vcodec copy {VIDEO_OUTPUT_FILE}"
        # ffmpeg -i videoCapture.mp4 -t 00:00:08 -c copy videoCaptureTrimmed.mp4
        trim_cmd = f"ffmpeg -y -i {VIDEO_OUTPUT_FILE} -s 00:00:00 -t 00:00:08 -c copy {VIDEO_OUTPUT_FILE_TRIMMED}"

        OpenCvCamera._run_cmd(f"{raspi_cmd} | {ffmpeg_cmd}")
        OpenCvCamera._run_cmd(trim_cmd)

        # process has finished.  wait for the os to let go of the camera
        time.sleep(0.5)
        log.info("done capturing video")

    @staticmethod
    def _run_cmd(cmd_str):
        log.info(f"run_cmd: {cmd_str}")
        try:
            subprocess.run(
                f"{cmd_str}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            log.error(f"error running {cmd_str}: {e}")
            OpenCvCamera.video_capture_error = e

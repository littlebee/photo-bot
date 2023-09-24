#!/usr/bin/env python3

# To see CV debug information, do
#
#    OPENCV_VIDEOIO_DEBUG=1 debug/test-hiresPhotoCapture.py

# Python program to save a video using OpenCV and output FPS
#
# from https://www.geeksforgeeks.org/saving-a-video-using-opencv/
import sys
import cv2

OUTPUT_FILE = "testPhotoCapture.jpg"
SIZE = (2048, 1536)

video_channel = 0
if len(sys.argv) > 1:
    video_channel = int(sys.argv[1])


# Create an object to read
# from camera
video = cv2.VideoCapture(video_channel)

# We need to check if camera
# is opened previously or not
if video.isOpened() is False:
    raise RuntimeError("Error reading video file")

video.set(cv2.CAP_PROP_FRAME_WIDTH, SIZE[0])
video.set(cv2.CAP_PROP_FRAME_HEIGHT, SIZE[1])
# video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
# video.set(cv2.CAP_PROP_FPS, 30)

capture_fps = video.get(cv2.CAP_PROP_FPS)

print(
    f"capturing image on video_channel={video_channel} SIZE={SIZE} capture_fps={capture_fps}",
)

ret, frame = video.read()

if ret is True:
    cv2.imwrite(OUTPUT_FILE, frame)

    print("The image was successfully saved.")
    print("")
    print("You can view the image captured with:")
    print(
        f"   scp pi@raspberrypi.local:/home/pi/photo-bot/{OUTPUT_FILE} . && open {OUTPUT_FILE}"
    )
    print("on your local machine")

else:
    raise RuntimeError(f"Error capturing image {ret}")

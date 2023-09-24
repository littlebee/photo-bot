#!/usr/bin/env python3

# To see CV debug information, do
#
#    OPENCV_VIDEOIO_DEBUG=1 debug/test-camera.py

# Python program to save a video using OpenCV and output FPS
#
# from https://www.geeksforgeeks.org/saving-a-video-using-opencv/
import sys
import time

import cv2

OUTPUT_FILE = "testVideoCapture.mp4"
SIZE = (2048, 1152)
DURATION = 10

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
video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
# video.set(cv2.CAP_PROP_FPS, 30)

capture_fps = video.get(cv2.CAP_PROP_FPS)

print(
    f"starting video_channel={video_channel} SIZE={SIZE} capture_fps={capture_fps}",
)

print(f"recording {DURATION} secs of video...")
start = time.time()
num_frames = 0
captured_frames = []
while True:
    ret, frame = video.read()

    if ret is True:
        # Write the frame into the
        # file 'filename.avi'
        # writer.write(frame)
        captured_frames.append(frame)
        num_frames += 1

    # Break the loop
    else:
        print(f"Error capturing image {ret}")
        break

    # runs for 30s
    if time.time() - start >= DURATION:
        break
    # if num_frames > 1000:
    #     break

actual_duration = time.time() - start
print(
    f"recorded {num_frames} frames in {actual_duration}s ({num_frames/actual_duration:.2f} fps)"
)

print(f"\nSaving video to {OUTPUT_FILE}")
# Below VideoWriter object will create
# a frame of above defined The output
# is stored in 'filename.avi' file.
start = time.time()

writer = cv2.VideoWriter(
    OUTPUT_FILE, cv2.VideoWriter_fourcc(*"mp4v"), capture_fps, SIZE
)
for frame in captured_frames:
    writer.write(frame)

actual_duration = time.time() - start
print(
    f"saved {num_frames} frames in {actual_duration}s ({num_frames/actual_duration:.2f} fps)"
)


# When everything done, release
# the video capture and video
# write objects
video.release()
writer.release()


print("The video was successfully saved.")
print("")
print("You can view the video recorded with:")
print(
    f"   scp pi@raspberrypi.local:/home/pi/photo-bot/{OUTPUT_FILE} . && open {OUTPUT_FILE}"
)
print("on your local machine")

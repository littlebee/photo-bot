#!/bin/bash

# this script is meant to be run from your local development machine,
# in the scatbot project root dir


if [ "$1" == "" ]; then
  echo "Error: missing parameter.  usage: ./upload.sh [USER@]IP_ADDRESS_OR_NAME"
  echo "   ex:  ./upload.sh pi@raspberrypi.local"
  exit 1
fi

targetUser=pi

if [ "$2" != "" ]; then
  targetUser=$2
  echo "got user"
  echo $targetUser
fi

# echo on
set -x

# stop on errors
set -e

TARGET_DIR="/home/$targetUser/photo-bot"
TARGET_HOST=$1

rsync --progress --partial \
--exclude=camera_test_output.mp4 \
--exclude=hires_test_photo.jpg \
--exclude=testVideoCapture.mp4 \
--exclude=testPhotoCapture.jpg \
--exclude=data/ \
--exclude=logs/ \
--exclude=.git -avz \
--exclude=__pycache__/ \
--exclude=.pytest_cache \
--exclude=.mypy_cache \
--exclude=.github \
. $TARGET_HOST:$TARGET_DIR


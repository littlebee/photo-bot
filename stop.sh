#!/bin/bash

# don't stop on error - let other subs exit if any sub fails to exit
# set -e

# user=`echo $USER`
# if [ "$user" != "root" ]; then
#   echo "Script must be run as root.  Try 'sudo ./stop.sh'"
#   exit 1
# fi

echo "stopping photo-bot"

pid_file="./photo-bot.pid"
if [[ "photo-bot" == *".pid" ]]; then
  pid_file="./photo-bot"
fi

if [ -f "$pid_file" ]; then
  kill -1 `cat $pid_file`
  rm -f $pid_file
else
  echo "$pid_file does not exist. skipping"
fi
/Users/bee/projects/scatbot/setup.cfg
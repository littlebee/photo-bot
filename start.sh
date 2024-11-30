#!/bin/bash

mkdir -p ./logs

user=`echo $USER`
if [ "$user" != "root" ]; then
  echo "Script must be run as root.  You are running as {$user}.  Try 'sudo ./start.sh'"
  exit 1
fi

echo "starting photo-bot"

# echo on from here may be a bad ideo
set -x

logfile="./photo-bot.log"

if [ -f "$logfile" ]; then
  mv -f "$logfile" "$logfile".1
fi

echo "starting photo-bot at $(date)" >> "$logfile"

python3 src/photo-bot.py > $logfile 2>&1 &

echo $! > ./photo-bot.pid

if [[ $sleep > 0 ]]; then
  echo "sleeping for $sleep seconds"
  sleep $sleep
fi

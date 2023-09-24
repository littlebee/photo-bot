#!/bin/bash

mkdir -p ./logs


# user=`echo $USER`
# if [ "$user" != "root" ]; then
#   echo "Script must be run as root.  Try 'sudo ./start.sh'"
#   exit 1
# fi

sleep=2

echo "starting photo-bot"

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

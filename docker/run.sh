#!/bin/bash
if [[ $MODE = 'DETECTION' ]];
then
  echo "Current task is video stream moving detection !"
  python3 /app/MovingDetection/VideoMovingDetection/run.py
elif [[ $MODE = 'DELETION' ]];
then
  echo "Current task is delete old picture !"
  python3 /app/MovingDetection/DeleteFilesInBucket/run.py
else
  echo "Do nothing !"
fi


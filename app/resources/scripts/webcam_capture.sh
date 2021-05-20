#!/bin/bash
while [[ 1 ]]; do
  fswebcam -r 1280x960 --no-banner /home/pi/snapshots/camtest.jpg
  sleep 5
done
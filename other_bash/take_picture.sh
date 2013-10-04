#!/bin/bash
ts=`date +%F_%R`
dir=/home/mediocregopher/Pictures/Webcam
mkdir -p $dir
bash -c "
ffmpeg -f video4linux2 -s vga -i /dev/video0 -vframes 5 $dir/$ts.%d.jpg >/dev/null 2>/dev/null
rm -f $dir/*.1.jpg
rm -f $dir/*.2.jpg
rm -f $dir/*.3.jpg
rm -f $dir/*.4.jpg" &
exit 0

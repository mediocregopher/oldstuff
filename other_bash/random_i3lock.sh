#!/bin/sh

H=/home/mediocregopher
R=`find $H/Wallpapers | grep -P 'png$' | sort -R | head -n1`

i3lock -i $R

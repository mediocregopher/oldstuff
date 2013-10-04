#!/bin/sh

RET=`curl 'http://gainesville.craigslist.org/sss/' 2>/dev/null | grep "$1"`
if [ "$RET" != "" ]; then
    echo "found"
fi

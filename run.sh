#!/bin/bash

source /etc/profile

base_dir=$(cd "$(dirname "$0")"; pwd)

# start token-server
cd $base_dir

cur_dir=$(pwd)
if [ ! -d log ]; then
   mkdir log
fi

#nohup gunicorn -w 2 CacheServer.wsgi:application -b 0.0.0.0:13060 -t 4 -k gevent > $base_dir/log/server.log 2>&1 &
gunicorn -w 4 iNaviUser.wsgi:application -b 0.0.0.0:8001 -t 4 -k gevent 

#nohup python $cur_dir/name_parser.py >log/name_predict.log 2>&1 &

if [ $? != 0 ]; then
    echo "Error happend when start token server"
    exit
fi

echo "Done"

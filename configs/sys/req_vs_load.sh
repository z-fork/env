#!/bin/sh
last_minute=`date +%d/%b/%Y:%H:%M --date="-1 minute"`
log_address=/home/kratos/log/nginx/access.log
nginx_load=`grep -c $last_minute $log_address`
mem=`free -g | grep buffers/ | awk '{print $3}'`
echo `date +%d/%b/%Y:%T` "| last_minute_nginx_load:" $nginx_load "| cpu_avg_load:" `awk '{print $1}' /proc/loadavg` "| mem_load(G):" $mem
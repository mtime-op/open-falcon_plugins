#!/usr/bin/env bash

domainname=$1
_PWD=$(pwd)
base_url="/home/mtime/logs/accesslog/"
base_error_url="/home/mtime/logs/serverlog/nginx/error.log"
now_flag_time=$(date -d "1 minutes ago" +'%M')
now_time=$(date -d "1 minutes ago" +'%Y:%H:%M')
full_format_nowtime=$(date -d "1 minutes ago" +'%Y%m%d%H%M')
full_format_errornowtime=$(date +"%Y/%m/%d %H:%M")
del_time=$(date  +'%H%M')

cd ${base_url}
if [ "X${now_flag_time}" == "X59" ];then
    temp_mulu=$(echo -n $(ls -ltr ${domainname}/*|tail -n 2 |awk '{print $NF}'))
    for tmulu in ${temp_mulu};do
        grep ${now_time} ${tmulu}|grep -v "favicon.ico">>/tmp/nginx_accesslog.${now_time}
    done
    mulu="/tmp/nginx_accesslog.${now_time}"
else
    mulu=$(ls -ltr ${domainname}/*|tail -n 1|awk '{print $NF}')
fi
#PV  平均耗时
temp_message1=$(grep ${now_time} ${mulu}|grep -v "favicon.ico"|awk -F '" "' '{print $(NF-1)}'|sed -e 's#"##g'|awk '{ORS="";sum +=$1;count +=1}END{if(count != 0){printf count" "sum/count} else {printf 0" "0}}');
temp_message1_pv=$(echo ${temp_message1}|awk '{print $1}');
temp_message1_taketime=$(echo ${temp_message1}|awk '{print $2}');
#4xx5xx个数
temp_message3_part1=$(echo -n "$(grep ${now_time} ${mulu}|grep -v 'favicon.ico'|awk '{if(($11 ~ /^[4|5]/)&&($11 !~ /403|499|400/))print $11}'|wc -l)");
#满请求个数
temp_message4=$(echo -n "$(grep ${now_time} ${mulu}|grep -v "favicon.ico"|awk -F '" "' '{if($(NF-1)>=10)print $0}'|wc -l)")
#错误数
temp_message0=$(echo -n "$(grep $(date -d "1 minutes ago" +'%H:%M') ${base_error_url}|grep 'Connection timed out'|grep -v 'access forbidden by rule'|grep -v 'limiting requests'|awk '$NF ~ /"'${domainname}'/{print $0}'|wc -l)")

#错误数+4xx5xx个数
temp_message3=$(echo -n "$((${temp_message3_part1}+${temp_message0}))")

echo ${temp_message1_pv}" "${temp_message1_taketime}" "${temp_message3_part1}" "${temp_message4}" "${temp_message3}" "${temp_message0}
if [ -f /tmp/nginx_accesslog.${now_time} ];then
    rm -rf /tmp/nginx_accesslog.${now_time}
fi
cd ${_PWD}

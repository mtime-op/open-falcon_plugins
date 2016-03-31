# encoding=utf-8
'''
本脚本是为了将nginx的分析结果推送到open-falcon中。推送的数据为：
#PV  平均耗时 4xx5xx个数 慢请求个数 错误数 错误数+4xx5xx个数
利用crontab 来调用脚本  每分钟一次。
nginx日志分析采用shell脚本实现。
shell脚本将结果echo出来，python脚本标准输出接收，然后经过编码push到falcon中。
'''

import os, time, logging, subprocess, socket
import requests, json

logging.basicConfig(level=logging.INFO, filemode="a+",
                    format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s",
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename="log/nginx_pushtofalcon.log"
                    )

nowtime = int(time.time())  # 获取程序运行的时间戳
baseurl = "/home/mtime/logs/accesslog"
dirnames = os.listdir(baseurl)
hostname = socket.gethostname()
mesg_pv = 0
mesg_avgtime = 0
mesg_4xx5xx = 0
mesg_slow = 0
mesg_error = 0
mesg_45error = 0
for index in xrange(len(dirnames)):
    dir_name = dirnames[index]
    command = "/bin/bash shell/nginx_log_hits.sh " + dir_name
    mesg = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_mesg = mesg.stdout.read()
    logging.info(stdout_mesg)
    stderror_mesg = mesg.stderr.read()
    if stderror_mesg != "" or stderror_mesg is not None:
        logging.error(stderror_mesg)
    if stdout_mesg is not None:
        mesg_pv = int(stdout_mesg.split(" ")[0])
        mesg_avgtime = float(stdout_mesg.split(" ")[1])
        mesg_4xx5xx = int(stdout_mesg.split(" ")[2])
        mesg_slow = int(stdout_mesg.split(" ")[3])
        mesg_error = int(stdout_mesg.split(" ")[4])
        mesg_45error = int(stdout_mesg.split(" ")[5])

    # 字典组装
    mesg_json = [
        {
            "endpoint": hostname,
            "metric": dir_name + "_pv",
            "timestamp": nowtime,
            "step": 60,
            "value": mesg_pv,
            "counterType": "GAUGE",
            "tags": "idc=jx,product=sevenlayer-api",
        },
        {
            "endpoint": hostname,
            "metric": dir_name + "_avgtime",
            "timestamp": nowtime,
            "step": 60,
            "value": mesg_avgtime,
            "counterType": "GAUGE",
            "tags": "idc=jx,product=sevenlayer-api",
        },
        {
            "endpoint": hostname,
            "metric": dir_name + "_4xx5xx",
            "timestamp": nowtime,
            "step": 60,
            "value": mesg_4xx5xx,
            "counterType": "GAUGE",
            "tags": "idc=jx,product=sevenlayer-api",
        },
        {
            "endpoint": hostname,
            "metric": dir_name + "_slow",
            "timestamp": nowtime,
            "step": 60,
            "value": mesg_slow,
            "counterType": "GAUGE",
            "tags": "idc=jx,product=sevenlayer-api",
        },
        {
            "endpoint": hostname,
            "metric": dir_name + "_error",
            "timestamp": nowtime,
            "step": 60,
            "value": mesg_error,
            "counterType": "GAUGE",
            "tags": "idc=jx,product=sevenlayer-api",
        },
        {
            "endpoint": hostname,
            "metric": dir_name + "_45error",
            "timestamp": nowtime,
            "step": 60,
            "value": mesg_45error,
            "counterType": "GAUGE",
            "tags": "idc=jx,product=sevenlayer-api",
        },
    ]
    logging.info("mesg_json: " + str(mesg_json))
    r = requests.post("http://127.0.0.1:1988/v1/push", data=json.dumps(mesg_json))
    print r.text

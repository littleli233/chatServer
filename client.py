import requests
from json import dumps, loads
from os import path
import time

profile = None
if not path.exists("clientprofile.json"):
    with open("clientprofile.json", "w+") as f:
        host = input("服务器地址:")
        username = input("用户名:")
        passwd = input("密码:")
        f.write(dumps({
            "host": host,
            "username": username,
            "passwd": passwd
        }))
        reg = requests.post("%s/reg" % host, json={"username": username, "passwd": passwd})
        print(reg.content)

with open("clientprofile.json", "r") as f:
    profile = loads(f.read())

print(
    """命令
    send [消息内容] 发送消息
    getmsg [int:消息数] 获取最近n条消息
    exit 退出
    """
)
while True:
    stin = input(" $ ")
    if stin == "exit":
        break
    elif "send" in stin:
        msg_ = stin.split(" ")[1:]
        msg = ""
        for i in  msg_:
            msg = "%s %s" % (msg, i)
        package = {
            "username": profile["username"],
            "passwd": profile["passwd"], 
            "context": msg,
            "time": time.time()
        }
        r = requests.post("%s/send" % profile["host"], json=package)
        print(r.content)

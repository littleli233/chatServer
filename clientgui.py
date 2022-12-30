import tkinter as tk
import requests
from os import path
from json import dumps, loads
from time import time, sleep, localtime, strftime
from functools import partial
from threading import Thread

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
        reg = requests.post("%s/reg" % host, json={"username": username, "passwd": passwd}, verify=False)
        print(reg.content)

with open("clientprofile.json", "r") as f:
    profile = loads(f.read())


def sendmsg():
    package = {
        "username": profile["username"],
        "passwd": profile["passwd"],
        "time": time(),
        "context": entry.get()
    }
    requests.post("%s/send" % profile["host"], json=package, verify=False)

def getmsg():
    package = {
        "username": profile["username"],
        "passwd": profile["passwd"],
    }
    msg_pass = None
    msg_pass_time = None
    print("start getmsg")
    response = requests.post("%s/getmsg-stream" % profile["host"], json=package, verify=False, stream=True)
    for line in response.iter_lines():
        msg = loads(line)
        text.get("end")
        try:
            if msg[2] == msg_pass and msg[1] == msg_pass_time:
                continue
            print(line)
            text.insert("end", "%s\n%s:%s\n" % (strftime("%Y-%m-%d %H:%M:%S", localtime(float(msg[1]))), msg[0], msg[2]))
            msg_pass = msg[2]
            msg_pass_time = msg[1]
        except IndexError:
            print("Get message failed")


window = tk.Tk()
window.title("chatClient")
window.geometry("400x600")

text = tk.Text(window, height=32)
# text.config(state=tk.DISABLED)
text.pack()
frame1 = tk.Frame(window)
frame1.pack()

entry = tk.Entry(frame1)
entry.grid(row=0, column=0)
button = tk.Button(frame1, text="发送", height=1, command=partial(sendmsg))
button.grid(row=0, column=1)

getT = Thread(target=getmsg)
getT.start()

window.mainloop()
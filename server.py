from flask import Flask, request, Response
from markupsafe import escape
from json import dumps, loads
import csv
from sys import argv
from os import path
from time import time, sleep


server = Flask(__name__)
if not path.exists("users.csv"):
    with open("users.csv", "w+") as f:
        f.close()
if not path.exists("message.csv"):
    with open("message.csv", "w+") as f:
        csv_ = csv.writer(f)
        csv_.writerow(["server", time(), "欢迎使用聊天服务器"])


@server.route("/")
def server_hello():
    return "server started"


@server.route("/api-version")
def api_version():
    return "2"


@server.route("/reg", methods=["POST"])
def register():
    print(request.json)
    username = request.json.get("username")
    passwd = request.json.get("passwd")
    csv_ = []
    with open("users.csv", "r") as f:
        c = csv.reader(f)
        for row in c:
            csv_.append(row)
            if username == row[0]:
                return dumps({"username": username, "passwd": passwd, "status": 1})
    with open("users.csv", "w") as f:
        c = csv.writer(f)
        csv_.append([username, passwd, 0])
        print(csv_)
        c.writerows(csv_)
        f.close()
    user = {"username": username, "passwd": passwd, "status": 0}
    return dumps(user)

@server.route("/send", methods=["POST"])
def send():
    pack = request.json
    with open("users.csv", "r") as f:
        c = csv.reader(f)
        for row in c:
            if row[0] == pack.get("username"):
                if row[2] == "0":
                    if row[1] == pack.get("passwd"):
                        writemsg(pack)
                        f.close()
                        return dumps({"status": 0})
            else:
                continue
        f.close()
        return dumps({"status": 1})


@server.route("/getmsg/<int:msgamount>", methods=["POST"])
def getmsg(msgamount):
    pack = request.json
    with open("users.csv", "r") as f:
        c = csv.reader(f)
        for row in c:
            if row[0] != pack.get("username"):
                continue
            else:
                if row[2] == "0":
                    if row[1] == pack.get("passwd"):
                        csv_ = []
                        with open("message.csv", "r") as f:
                            c = csv.reader(f)
                            for row in c:
                                csv_.append(row)
                        if -len(csv_) + msgamount >= 0:
                            return dumps(csv_[len(csv_)-1:0:-1])
                        else:
                            return dumps(csv_[len(csv_)-1:len(csv_)-1-msgamount:-1])
                
        return {"status": 1}

@server.route("/getmsg-stream", methods=["POST"])
def getmsg_stream():
    pack = request.json
    with open("users.csv", "r") as f:
        c = csv.reader(f)
        for row in c:
            if row[0] != pack.get("username"):
                continue
            else:
                if row[2] == "0":
                    if row[1] == pack.get("passwd"):
                        return Response(action_getmsg(), mimetype="text")

def action_getmsg():
    pass_msg = None
    while True:
        csv_ = []
        with open("message.csv", "r") as f:
            c = csv.reader(f)
            for row in c:
                csv_.append(row)
        sleep(0.1)
        pass_msg = csv_[-1]
        yield dumps(csv_[-1]) + "\n"
    
    
def writemsg(msg):
    csv_ = []
    with open("message.csv", "r") as f:
        c = csv.reader(f)
        times = 0
        for row in c:
            if times > 99:
                break
            csv_.append(row)
            times += 1
        f.close()

    with open("message.csv", "w") as f:
        c = csv.writer(f)
        csv_.append([msg.get("username"), msg.get("time"), msg.get("context")])
        c.writerows(csv_)
        f.close()

if not path.exists("serverprofile.json"):
    with open("serverprofile.json", "w+") as f:
        f.write(dumps({
            "host": "0.0.0.0",
            "port":10081,
            "ssl": False, 
            "ssl_crt": "",
            "ssl_key": "",
            "debug": False,
            "allow_reg": True
        }))
profile = None
with open("serverprofile.json", "r") as f:
    profile = loads(f.read())

if profile["ssl"]:
    server.run(profile["host"], profile["port"], debug=profile["debug"], ssl_context=(profile["ssl_crt"], profile["ssl_key"]))
else:
    server.run(profile["host"], profile["port"], debug=profile["debug"])

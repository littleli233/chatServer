from flask import Flask, request
from markupsafe import escape
from json import dumps, loads
import csv


server = Flask(__name__)


@server.route("/")
def server_hello():
    return "server started"


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

@server.route("/getmsg/<int:msgamount>")
def getmsg(msgamount):
    csv_ = []
    with open("message.csv", "r") as f:
        c = csv.reader(f)
        for row in c:
            csv_.append(row)
    return dumps(csv_[-101:-101+msgamount])

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

server.run("0.0.0.0", 10081, debug=True)

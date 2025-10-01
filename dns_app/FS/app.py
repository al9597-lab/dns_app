from flask import Flask, request, jsonify, Response
import socket
import os
import json

app = Flask(__name__)
FS_PORT = int(os.environ.get("FS_PORT", "9090"))

def fib(n):
    a = 0
    b = 1
    i = 0
    while i < n:
        a, b = b, a + b
        i += 1
    return a

def udp_send(ip, port, text):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(text.encode("utf-8"), (ip, int(port)))
        s.settimeout(1.0)
        try:
            s.recvfrom(1024)
        except:
            pass
    finally:
        s.close()

@app.route("/register", methods=["PUT"])
def register():
    try:
        body = request.get_json(force=True)
    except:
        return Response("Bad JSON", status=400)

    need = ["hostname", "ip", "as_ip", "as_port"]
    for k in need:
        if k not in body:
            return Response("Missing {}".format(k), status=400)

    hostname = str(body["hostname"])
    fs_ip = str(body["ip"])
    as_ip = str(body["as_ip"])
    as_port = str(body["as_port"])

    msg = "TYPE=A\nNAME={}\nVALUE={}\nTTL=10\n".format(hostname, fs_ip)

    try:
        udp_send(as_ip, as_port, msg)
    except Exception as e:
        return Response("Registration failed: {}".format(e), status=500)

    return Response("Registered", status=201)

@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    x = request.args.get("number", None)
    if x is None:
        return Response("Missing number", status=400)

    try:
        n = int(x)
    except:
        return Response("number must be integer", status=400)

    if n < 0:
        return Response("number must be non-negative", status=400)

    value = fib(n)
    return jsonify({"fibonacci": value})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FS_PORT)

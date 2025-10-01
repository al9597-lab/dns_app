from flask import Flask, request, Response
import socket
import requests
import os

app = Flask(__name__)
US_PORT = int(os.environ.get("US_PORT", "8080"))

def dns_query(as_ip, as_port, hostname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2.0)
    try:
        q = "TYPE=A\nNAME={}\n".format(hostname)
        s.sendto(q.encode("utf-8"), (as_ip, int(as_port)))
        data, _ = s.recvfrom(2048)
    except Exception as e:
        s.close()
        return None
    s.close()

    text = data.decode("utf-8", errors="ignore")
    ip = None
    for line in text.splitlines():
        if line.startswith("VALUE="):
            ip = line.split("=", 1)[1].strip()
            break
    return ip

@app.route("/fibonacci", methods=["GET"])
def proxy_fibonacci():
    hostname = request.args.get("hostname")
    fs_port  = request.args.get("fs_port")
    number   = request.args.get("number")
    as_ip    = request.args.get("as_ip")
    as_port  = request.args.get("as_port")

    # 缺参 → 400
    if not hostname or not fs_port or not number or not as_ip or not as_port:
        return Response("Bad Request: missing parameters", status=400)

    try:
        int(number)
    except:
        return Response("Bad Request: number must be integer", status=400)

    ip = dns_query(as_ip, as_port, hostname)
    if not ip:
        return Response("DNS query failed", status=500)

    url = "http://{}:{}/fibonacci?number={}".format(ip, fs_port, number)
    try:
        r = requests.get(url, timeout=3)
        return Response(r.text, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        return Response("FS request failed: {}".format(e), status=502)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=US_PORT)

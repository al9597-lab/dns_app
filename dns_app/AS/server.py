import socket
import json
import os

AS_PORT = int(os.environ.get("AS_PORT", "53533"))
RECORD_FILE = os.environ.get("RECORD_FILE", "dns_records.json")

def load_db():
    if not os.path.exists(RECORD_FILE):
        return {}
    try:
        with open(RECORD_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(db):
    with open(RECORD_FILE, "w") as f:
        json.dump(db, f)

def parse_message(text):
    d = {}
    for line in text.splitlines():
        line = line.strip()
        if line == "":
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            d[k.strip().upper()] = v.strip()
    return d

def format_answer(name, value, ttl):
    return "TYPE=A\nNAME={}\nVALUE={}\nTTL={}\n".format(name, value, ttl)

def main():
    db = load_db()  
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", AS_PORT))
    print("[AS] listening UDP on 0.0.0.0:{}".format(AS_PORT))

    while True:
        data, addr = sock.recvfrom(2048)
        text = data.decode("utf-8", errors="ignore")
        req = parse_message(text)

        if req.get("TYPE") == "A" and "NAME" in req and "VALUE" in req and "TTL" in req:
            name = req["NAME"]
            value = req["VALUE"]
            ttl = int(req["TTL"])
            db[name] = {"value": value, "ttl": ttl}
            save_db(db)
            try:
                sock.sendto(b"OK\n", addr)
            except:
                pass
            print("[AS] registered: {} -> {} (ttl={})".format(name, value, ttl))

        elif req.get("TYPE") == "A" and "NAME" in req and "VALUE" not in req:
            name = req["NAME"]
            if name in db:
                value = db[name]["value"]
                ttl = db[name]["ttl"]
                ans = format_answer(name, value, ttl)
                sock.sendto(ans.encode("utf-8"), addr)
                print("[AS] query ok: {} -> {}".format(name, value))
            else:
                sock.sendto(b"", addr)
                print("[AS] query miss: {}".format(name))
        else:
            print("[AS] bad message from {}:\n{}".format(addr, text))

if __name__ == "__main__":
    main()

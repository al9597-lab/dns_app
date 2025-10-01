# 📘 DNS Application – Simplified Authoritative Server

##  Project Structure

```
dns_app/
├─ AS/                  # Authoritative Server (UDP 53533)
│   ├─ server.py
│   ├─ Dockerfile
│   └─ requirements.txt
│
├─ FS/                  # Fibonacci Server (HTTP 9090)
│   ├─ app.py
│   ├─ Dockerfile
│   └─ requirements.txt
│
├─ US/                  # User Server (HTTP 8080)
    ├─ app.py
    ├─ Dockerfile
    └─ requirements.txt


```

---

### 1. Build images
```bash
docker build -t as:lite AS
docker build -t fs:lite FS
docker build -t us:lite US
```

### 2. Create a network
```bash
docker network create dnsnet
```

### 3. Start the containers
```bash
docker run -d --name as --network dnsnet -p 53533:53533/udp as:lite
docker run -d --name fs --network dnsnet -p 9090:9090       fs:lite
docker run -d --name us --network dnsnet -p 8080:8080       us:lite
```

---

##  Register FS with AS

Before the User Server can query the Fibonacci Server, FS must register its hostname and IP with AS.

```bash
curl -X PUT http://localhost:9090/register   -H "Content-Type: application/json"   -d '{"hostname":"fibonacci.com","ip":"fs","as_ip":"as","as_port":"53533"}' -i
```



---

##  Query Fibonacci via US

Now the US will resolve the hostname using AS, then forward the request to FS:

```bash
curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as&as_port=53533" -i
```



---

##  Test Error Handling

- Missing parameters → `400 Bad Request`  
```bash
curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10"
```

- Non-integer number → `400 Bad Request`  
```bash
curl "http://localhost:9090/fibonacci?number=oops"
```

- Successful request → `200 OK`  
```bash
curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=7&as_ip=as&as_port=53533"
```

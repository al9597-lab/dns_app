FROM python:3.11-slim
WORKDIR /app
COPY server.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true
EXPOSE 53533/udp
ENV AS_PORT=53533
CMD ["python", "server.py"]

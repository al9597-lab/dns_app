FROM python:3.11-slim
WORKDIR /app
COPY app.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 9090
ENV FS_PORT=9090
CMD ["python", "app.py"]

FROM python:3.13-slim

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        sane-utils \
        libsane1 \
        scanbd \
        cifs-utils \
        netpbm \
        ghostscript \
        poppler-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p /app/scan

COPY ./requirements.txt /app
COPY ./scanserver.py /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scanserver.py"]

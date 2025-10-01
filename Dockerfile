FROM python:3.13-slim

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        sane-utils \
        libsane1 \
        scanbd \
        cifs-utils \
        netpbm \
        ghostscript \
        poppler-utils \
        libtiff-tools && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Verzeichnisse für Scans + Temp
RUN mkdir -p /app/scan /app/tmp

COPY ./requirements.txt /app
COPY ./scanserver.py /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scanserver.py"]

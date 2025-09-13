FROM python

RUN apt-get update -y && \ 
    apt-get install sane-utils scanbd cifs-utils netpbm ghostscript -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app
COPY scanserver.py /app

RUN pip install -r requirements.txt

CMD  ["python", "scanserver.py"]

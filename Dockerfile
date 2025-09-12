FROM python

RUN apt-get update -y && \ 
    apt-get install sane-utils scanbd cifs-utils netpbm ghostscript -y && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY scanserver.py ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "scanserver.py"]

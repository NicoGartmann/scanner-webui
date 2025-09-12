FROM python

COPY requirements.txt ./
COPY scanserver.py ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "scanserver.py"]

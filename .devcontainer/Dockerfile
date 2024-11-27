FROM docker.io/library/python@sha256:5c73034c2bc151596ee0f1335610735162ee2b148816710706afec4757ad5b1e 

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN apt update && apt install -y iputils-ping  jq curl

WORKDIR /client

# this will start __main__.py
CMD ["python3", "."]
FROM hrishi2861/terabox:latest
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install aria2
RUN pip3 install aria2p
RUN pip3 install -r requirements.txt

COPY . .
CMD ["bash", "run.sh"]

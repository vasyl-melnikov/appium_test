FROM robd003/python3.10

#RUN apt-get update && \
#    apt-get install -y python3.10 python3-pip
#
#RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

RUN python3 -m pip install --upgrade pip

WORKDIR /app
COPY . /app/

RUN pip install -r /app/requirements.txt

# Run the consumer.py script when the container starts
CMD ["python3", "main.py"]

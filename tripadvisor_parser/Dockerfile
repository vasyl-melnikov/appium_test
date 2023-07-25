FROM robd003/python3.10

RUN python3 -m pip install --upgrade pip

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app/

CMD ["python3", "main.py"]

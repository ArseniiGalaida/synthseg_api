FROM python:3.8-slim

WORKDIR /

COPY . /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "handler.py"]
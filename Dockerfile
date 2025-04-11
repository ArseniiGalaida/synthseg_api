FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY . /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python3 app/download_model.py

CMD ["python", "handler.py"]
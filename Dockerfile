FROM python:3.7.2-slim

COPY . /app
COPY . /requirements.txt
WORKDIR /app

RUN pip install --upgrade pip 

RUN pip install >> requirements.txt


ENTRYPOINT ["python", "app.py"]

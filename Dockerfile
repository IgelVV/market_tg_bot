FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install nano

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY market .

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

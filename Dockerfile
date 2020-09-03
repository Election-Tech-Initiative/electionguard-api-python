FROM python:3.8
ENV host 0.0.0.0

RUN apt update && apt-get install -y \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev
RUN pip install pipenv

COPY ./Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./app /app

EXPOSE 8000
CMD uvicorn app.main:app --host "$host" --port 8000
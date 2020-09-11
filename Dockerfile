FROM python:3.8 AS base
ENV host 0.0.0.0
ENV port 8000
RUN apt update && apt-get install -y \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev
RUN pip install pipenv
COPY ./Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt

FROM base AS dev
VOLUME [ "/app" ]
EXPOSE $port
CMD uvicorn app.main:app --reload --host "$host" --port "$port"

FROM base AS prod
COPY ./app /app
EXPOSE $port
CMD uvicorn app.main:app --host "$host" --port "$port"

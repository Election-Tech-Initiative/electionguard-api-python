FROM python:3.8 AS base
ENV host 0.0.0.0
ENV port 8000
RUN apt update && apt-get install -y \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev
RUN pip install 'poetry==1.0.10'
COPY ./pyproject.toml /tmp/
COPY ./poetry.lock /tmp/
RUN cd /tmp && poetry export -f requirements.txt > requirements.txt
RUN pip install -r /tmp/requirements.txt

FROM base AS dev
VOLUME [ "/app" ]
EXPOSE $port
CMD uvicorn app.main:app --reload --host "$host" --port "$port"

FROM base AS prod
COPY ./app /app
EXPOSE $port
# TODO: We should not have to use the --reload flag here! See issue #80
CMD uvicorn app.main:app --reload --host "$host" --port "$port"

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9 AS base
ENV PORT 8000
RUN apt update && apt-get install -y \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev
RUN pip install 'poetry==1.1.6'
COPY ./pyproject.toml /tmp/
COPY ./poetry.lock /tmp/
RUN cd /tmp && poetry export -f requirements.txt > requirements.txt
RUN pip install -r /tmp/requirements.txt
EXPOSE $PORT

FROM base AS dev
VOLUME [ "/app/app" ]
CMD /start-reload.sh

FROM base AS prod
COPY ./app /app/app
# The base image will start gunicorn

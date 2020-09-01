FROM python:3.8
COPY . .
RUN apt update
RUN apt-get install libgmp-dev
RUN	apt-get install libmpfr-dev
RUN	apt-get install libmpc-dev
RUN pip install pipenv
RUN pipenv install
EXPOSE 8000
CMD pipenv run uvicorn app.main:app --host 0.0.0.0 --port 8000
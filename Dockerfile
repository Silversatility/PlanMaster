FROM python:3.6

RUN apt update
RUN apt install -y postgresql-client vim graphviz libgraphviz-dev libev-dev libevent-dev

RUN mkdir /code
WORKDIR /code
ADD src/backend/requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

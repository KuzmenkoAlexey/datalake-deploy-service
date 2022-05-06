FROM python:3.10.2 as production

RUN mkdir -p /usr/app

WORKDIR /usr/app

COPY requirements.txt /usr/app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY src /usr/app

CMD uvicorn --host 0.0.0.0 main:app


FROM production as development

COPY requirements-dev.txt /usr/app
RUN pip install --no-cache-dir -r requirements-dev.txt

CMD uvicorn --host 0.0.0.0 main:app
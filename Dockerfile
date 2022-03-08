# FROM python:3.9-bullseye
FROM python:3.9-slim
MAINTAINER SYSNET-CZ "info@sysnet.cz"

ARG HOME_DIR=/opt/opendata
ARG DATA_DIR=${HOME_DIR}/data
ARG CONF_DIR=${HOME_DIR}/conf

WORKDIR ${HOME_DIR}
RUN mkdir ${DATA_DIR}
RUN mkdir ${CONF_DIR}

COPY eap/ ${HOME_DIR}/
COPY requirements.txt ${HOME_DIR}/
COPY conf/ ${CONF_DIR}/

RUN chmod -R 644 ${HOME_DIR}
RUN chmod -R 755 ${HOME_DIR}/exporter.py
RUN chmod -R 755 ${HOME_DIR}/importer.py
RUN chmod -R 755 ${HOME_DIR}/scheduler.py
RUN chmod -R 644 ${CONF_DIR}

RUN apt-get update
RUN apt-get install -y mc curl iputils-ping

ENV SERVICE_ENVIRONMENT=production \
    EXPORT_DATA_DIR=${DATA_DIR} \
    CONFIG_DIR=${CONF_DIR} \
    ES_HOST_NAME=elasticsearch \
    ES_PORT=9200
# ENV ES_USER=elastic
# ENV  ES_PASSWORD=xxxxx

RUN python -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8080
HEALTHCHECK CMD curl -f http://localhost:8080/scheduler || exit 1
CMD ["gunicorn", "--preload", "app:app", "-w", "1", "-t", "120", "-b", "0.0.0.0:8080"]

# CMD ["python", "scheduler.py"]
# CMD /bin/bash

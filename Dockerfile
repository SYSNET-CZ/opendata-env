FROM python:3.9-bullseye
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
RUN chmod -R 644 ${CONF_DIR}

RUN apt-get update
RUN apt-get install -y mc curl iputils-ping

ENV EXPORT_DATA_DIR=${DATA_DIR} \
    CONFIG_DIR=${CONF_DIR} \
    ES_HOST_NAME=elasticsearch \
    ES_PORT=9200
# ENV ES_USER=elastic
# ENV  ES_PASSWORD=F8qfSQMmNC1oU1XD1oS4

RUN python -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "scheduler.py"]
# CMD /bin/bash

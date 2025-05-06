FROM python:3.12-slim


RUN mkdir -p /opt
RUN mkdir -p /data/indir
RUN mkdir -p /data/outdir


RUN chown -R 1000:1000 /data/indir /data/outdir /opt

RUN apt-get update && apt-get install -y  git build-essential make wget  zlib1g-dev libc6 pigz &&\
	pip install snakemake


# Build and install FLASH2, vidjil-algo and germline data
RUN git clone https://github.com/dstreett/FLASH2.git && \
	cd FLASH2 && make && mv flash2 /usr/local/bin/flash2

COPY vidjil-algo-2024.02 /usr/local/bin
COPY vidjil-algo-2025.02 /usr/local/bin

COPY germline /opt/germline
# germline folder should be accessible to user 1000:1000
RUN chown -R 1000:1000 /opt/germline

COPY vdj_filter.g /opt/germline/vdj_filter.g

COPY Snakefile /opt/Snakefile
COPY config.json /opt/config.json


ENV XDG_CACHE_HOME=/data/indir

WORKDIR /opt

COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

USER 1000:1000

ENTRYPOINT [ "/opt/entrypoint.sh" ]

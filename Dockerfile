FROM python:3.12-slim


RUN mkdir -p /opt
RUN mkdir -p /data/indir
RUN mkdir -p /data/outdir


RUN chown -R 1000:1000 /data/indir /data/outdir /opt

RUN apt-get update && apt-get install -y  git build-essential make wget  zlib1g-dev libc6 pigz &&\
	pip install snakemake


# Build and install FLASH2, vidjil-algo and germline data
RUN git clone https://github.com/dstreett/FLASH2.git && \
	cd FLASH2 && make && mv flash2 .. && cd .. &&\
	git clone https://gitlab.inria.fr/vidjil/vidjil.git &&\
	cd vidjil &&\
	git checkout release-2025.02 &&\
	make algo germline &&\
	mv germline .. && mv vidjil-algo .. && cd .. &&\
	cd germline && wget https://gitlab.inria.fr/vidjil/contrib/-/raw/master/preprocess/vdj_filter.g && cd .. &&\
	rm -r vidjil FLASH2


RUN mv flash2 /usr/local/bin/flash2
RUN mv vidjil-algo /usr/local/bin/vidjil-algo
RUN mv /germline /opt

# germline folder should be accessible to user 1000:1000
RUN chown -R 1000:1000 /opt/germline

COPY vdj_filter.g /opt/germline/vdj_filter.g

COPY Snakefile /opt/Snakefile
COPY config.json /opt/config.json

USER 1000:1000

ENV XDG_CACHE_HOME=/data/indir

WORKDIR /opt

ENTRYPOINT [ "bash", "-c"]

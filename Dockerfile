FROM ghcr.io/astral-sh/uv:python3.13-bookworm


RUN mkdir -p /opt
RUN mkdir -p /data/indir
RUN mkdir -p /data/outdir

RUN uv pip install --system snakemake

RUN chown 1000:1000 /data/indir
RUN chown 1000:1000 /data/outdir

COPY germline /opt/germline
RUN chown -R 1000:1000 /opt

COPY vidjil-algo /usr/local/bin/vidjil-algo
COPY flash2 /usr/local/bin/flash2

COPY Snakefile /opt/Snakefile
COPY config.json /opt/config.json

USER 1000:1000

ENV XDG_CACHE_HOME=/data/indir

WORKDIR /opt

ENTRYPOINT [ "snakemake", "-c", "8" ]

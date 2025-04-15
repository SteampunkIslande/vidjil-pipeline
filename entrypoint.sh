#!/bin/bash

snakemake -s /opt/Snakefile --configfile /opt/config.json --cores 16

rm -R /data/outdir/preprocess-flash

# Rename to be more user-friendly
mv /data/outdir/preprocess-prefilter /data/outdir/fastq-vidjil

rm /data/outdir/fastq-vidjil/*.vidjil.gz

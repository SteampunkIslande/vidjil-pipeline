#!/bin/bash

INDIR=$1
OUTDIR=$2

shift 2

if [ -z "$INDIR" ] || [ -z "$OUTDIR" ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    exit 1
fi
if [ ! -d "$INDIR" ]; then
    echo "Input directory does not exist: $INDIR"
    exit 1
fi
if [ ! -d "$OUTDIR" ]; then
    echo "Output directory does not exist: $OUTDIR"
    exit 1
fi

docker run -it --volume $INDIR:/data/indir --volume $OUTDIR:/data/outdir vidjil-pipeline:1.0.4 "$@"


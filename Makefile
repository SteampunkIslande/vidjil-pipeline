build:
	docker build . -t 'vidjil-pipeline:1.0.2'

run:
	docker run vidjil-pipeline:1.0.0 --volume ./data/indir:/data/indir ./data/outdir:/data/outdir


PHONY: build run 
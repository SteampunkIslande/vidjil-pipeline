# What's this?

This is just a repository holding the Snakefile and Dockerfile to generate [vidjil](https://www.vidjil.org/) results from a Fastq folder.
In the release section is the tar file for the docker image I built.

Please visit [vidjil](https://www.vidjil.org/) website if you want to know more.
I'm not a vidjil developer, this is just a convenience pipeline for other bioinformaticians like me.

Enjoy!

# Get this pipeline

## Prepare

The following script downloads all the necessary components for the vidjil-pipeline repo.
Run it from any folder on your Linux box, this will download everything into this repository's folder.


```bash
# cd to where you want this repo to be downloaded into

# Clone this repo
git clone git@github.com:SteampunkIslande/vidjil-pipeline

# Build flash2
cd vidjil-pipeline
git clone git@github.com:dstreett/FLASH2.git
cd FLASH2
make

# Move flash2 to this repo
mv flash2 ..; cd ..

wget 'https://www.vidjil.org/releases/vidjil-algo-latest.tar.gz' && tar -xvf vidjil-algo-latest.tar.gz

# Future-proof release date ;)
cd vidjil-algo-2024.02

# Build and install vidjil-algo and germline
make vidjil-algo germline && mv germline .. && mv vidjil-algo ..

# Get preprocess germline file
cd ../germline
wget https://gitlab.inria.fr/vidjil/contrib/-/raw/master/preprocess/vdj_filter.g

```

## Build the docker image

```bash
cd vidjil-pipeline
docker build . -t 'vidjil-pipeline:1.0.0'
```

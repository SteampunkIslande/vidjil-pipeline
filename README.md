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
git clone https://github.com:SteampunkIslande/vidjil-pipeline
```

This pipleine can be launch with a docker image. 
You need firt to build it and after that to run this iamge.


## Build the docker image

```bash
cd vidjil-pipeline
make build
```

## Run the docker image

To launch complete pipeline on all fastq.gz file available in `data/indir/Fastq/` directory, just launch following command:

```bash
make run
```


## Detailled step for docker build step or local use


### Build flash2

```bash
git clone https://github.com:dstreett/FLASH2.git
cd FLASH2
make
```

### Build vidjil algo and

```bash
git clone https://gitlab.inria.fr/vidjil/vidjil.git &&\
	cd vidjil &&\
	git checkout release-2025.02 &&\
	make algo germline &&\
	mv germline .. && mv vidjil-algo .. && cd .. 
```


### Get vidjil germline data

```bash
cd vidjil
make germline
mv germline ..
cd ../germline
wget https://gitlab.inria.fr/vidjil/contrib/-/raw/master/preprocess/vdj_filter.g
```
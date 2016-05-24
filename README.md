# amos-ss16-proj6
![Travis](https://api.travis-ci.org/AMOSus/amos-ss16-proj6.svg?branch=master)

## About This Project
FAU AMOS Group 6: Siemens AG

## Build Instructions

The standard way to use this product is to build a docker container and to run it on your machine.
If you do not want to or, for some reason, are not able to use docker, you should still be able to build our project: use a recent Ubuntu system and for the further setup mimic the steps in docker/Dockerfile and docker/docker-entrypoint.sh. However, you might, of course have to adapt to your specific setup at one place or the other. There is no detailed documentation about the second approach.

###Getting the Docker container:

By default each push to our GitHub repository triggers a build of the Docker container on TravisCI. The container is then uploaded to DockerHub. Therefore the easiest way to get the Docker container is to just pull it from the DockerHub. Use the following command:

**docker pull tobido/amos-ss16-pro6:latest**

If you want to build the container yourself (because you want to make changes that you do not want to publish on GitHub or for whatever reason) do the following:

1. Install docker
2. Clone the GitHub repository to \<path-to-some-directory\>
3. Change to \<path-to-some-directory\>
4. If necessary, grant yourself execution rights of the file /docker/build
5. Run /docker/build (the build file assumes that your current directory is the root of the repository, therefore step 3)


###Running the Docker container:

The basic comman is docker run \<container-name\>. There are plenty of command line options that you might want to use. Minimally you need the following:

--publish=\<port-on-host\>:80

Our web server offers its service on port 80 *inside* the docker container. Per default this port is not visible to the outside. In order to access it via ports on your host machine you have to use this option. That is, if you just want to offer the service on port 80, use --publish=80:80

-e 'CONTEXT_PATH=\<some-suffix-path\>' This is best explained via example: per default we offer our service at www.osr-group.de. However, not at the root path but rather at www.osr.group.de/ss16/proj6. In this case we have to set CONTEXT_PATH = /ss16/proj6. (Mind the leading slash here!)

So a minimal example usage would be

**docker run -e 'CONTEXT_PATH=/ss16/proj6' --publish=80:80 tobido/amos-ss16-proj6**


## Further Information
### Bill of Materials
https://github.com/AMOSus/amos-ss16-proj6/wiki/Bill-Of-Materials
### Database Schema
https://github.com/AMOSus/amos-ss16-proj6/wiki/Database-Schema
### Software Arichtecture
https://github.com/AMOSus/amos-ss16-proj6/wiki/Software-Architecture
### Detailed Information on Data Processing
https://github.com/AMOSus/amos-ss16-proj6/wiki/DataProcessing
### Detailed Information on the Frontend
https://github.com/AMOSus/amos-ss16-proj6/wiki/Frontend

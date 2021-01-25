FROM python:3.8
FROM wmhchallenge/sysu_media_2
#FROM wmhchallenge/pgs
#FROM ubuntu:20.04
#WORKDIR /segmentation
#COPY . .

#directory to store input/output/data
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
RUN mkdir  /flywheel/v0/input
RUN mkdir  /flywheel/v0/output
#RUN mkdir  ${FLYWHEEL}/input/pre
#RUN mkdir  ${FLYWHEEL}/input/orig

# Prepare environment
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    curl \
                    bzip2 \
                    ca-certificates \
                    xvfb \
                    cython3 \
                    build-essential \
                    autoconf \
                    libtool \
                    pkg-config \
                    jq \
                    zip \
                    unzip \
                    nano \
                    default-jdk \
                    git && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y --no-install-recommends \
                    nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install FSL
ENV FSLDIR="/usr/share/fsl"
RUN apt-get update -qq \
  && apt-get install -y -q --no-install-recommends \
         bc \
         dc \
         file \
         libfontconfig1 \
         libfreetype6 \
         libgl1-mesa-dev \
         libglu1-mesa-dev \
         libgomp1 \
         libice6 \
         libxcursor1 \
         libxft2 \
         libxinerama1 \
         libxrandr2 \
         libxrender1 \
         libxt6 \
         wget \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
  && echo "Downloading FSL ..." \
  && mkdir -p /usr/share/fsl \
  && curl -fsSL --retry 5 https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-5.0.9-centos6_64.tar.gz \
  | tar -xz -C /usr/share/fsl --strip-components 1

ENV PATH="${FSLDIR}/bin:$PATH"
ENV FSLOUTPUTTYPE="NIFTI_GZ"

# Install c3d
ENV C3DPATH="/opt/convert3d-nightly" \
    PATH="/opt/convert3d-nightly/bin:$PATH"
RUN echo "Downloading Convert3D ..." \
   && mkdir -p /opt/convert3d-nightly \
   && curl -fsSL --retry 5 https://sourceforge.net/projects/c3d/files/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz/download \
   | tar -xz -C /opt/convert3d-nightly --strip-components 1


# Install python packages
RUN pip install --no-cache flywheel-sdk \
 && pip install --no-cache docker \
 && pip install --no-cache pathlib 


#Copy files (FLAIR and T1)
#COPY FLAIR ${FLYWHEEL}/input/pre
#COPY T1 ${FLYWHEEL}/input/pre

#Volume to gain access to docker commands (hopefully)
#RUN apt-get -yqq update && apt-get -yqq install docker.io
#VOLUME /var/run/docker.sock

#copy script and manifest into docker container 
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY run.py ${FLYWHEEl}/run.py
COPY . ${FLYWHEEL}/

#COPY run.py ${FLYWHEEL}/run.py #Script goes here 
RUN chmod +x ${FLYWHEEL}/*
RUN chmod +x ${FLYWHEEL}/run.py
#RUN chmod +x ${FLYWHEEL}/src/*

#Preservation of flywheel engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh
RUN chmod +x ${FLYWHEEL}/docker-env.sh

#Workdirectory set
WORKDIR /flywheel/v0
ENTRYPOINT [ "python /flywheel/v0/run.py" ]
#/flywheel/v0

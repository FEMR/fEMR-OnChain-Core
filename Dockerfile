FROM ubuntu:latest

COPY . /opt/app
WORKDIR /opt/app

RUN apt-get update && apt-get install -y dos2unix
RUN find /opt/app -type f -exec dos2unix {} \;

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update -y && \
    ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime && \
    apt-get install -y tzdata && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get install unzip curl python3 python3-pip \
                    python3-dev libssl-dev python3-sphinx \
                    virtualenv -y && \
    apt-get upgrade -y
RUN pip3 install -r requirements.txt
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install nodejs -y

RUN /opt/app/build.sh all
RUN /opt/app/build.sh setup

EXPOSE 8081

ENTRYPOINT [ "/opt/app/build.sh", "run" ]

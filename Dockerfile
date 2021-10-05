FROM ubuntu:latest

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update -y && \
    ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime && \
    apt-get install -y tzdata && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get install unzip curl python3 python3-pip \
                    python3-dev libssl-dev python3-sphinx \
                    virtualenv libpq-dev -y && \
    apt-get upgrade -y
RUN pip3 install -r requirements.txt
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install nodejs -y

EXPOSE 8081

ENTRYPOINT [ "/build/build.sh", "init-all-run" ]

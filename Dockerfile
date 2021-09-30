FROM ubuntu:latest

RUN apt-get update -y && \
    apt-get install unzip apache2 python3 python3-pip mysql-server \
                    libmysqlclient-dev python3-dev libssl-dev python3-sphinx \
                    libpq-dev virtualenv -y && \
    apt-get upgrade -y && \
    pip3 install -r /home/vagrant/femr_onchain/requirements.txt && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt install nodejs

EXPOSE 8080
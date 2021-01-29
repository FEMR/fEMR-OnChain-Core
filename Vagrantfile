# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-20.04"

  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.network :forwarded_port, guest: 22, host: 2222, id: 'ssh'

  config.vm.synced_folder ".", "/home/vagrant/femr_onchain"

  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.memory = "1024"
  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get clean
    rm -rf /var/lib/apt/lists/*
    apt-get update
    apt-get install -y unzip apache2 python3 python3-pip mysql-server libmysqlclient-dev python3-dev libssl-dev python3-sphinx libpq-dev virtualenv
    apt-get upgrade -y
    pip3 install -r /home/vagrant/femr_onchain/requirements.txt
    curl -sL https://deb.nodesource.com/setup_14.x | bash -
    sudo apt install nodejs
  SHELL
end

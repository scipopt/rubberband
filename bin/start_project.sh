#! /bin/bash

# This is a script that will set up everything needed for rubberband development.
# `sudo` is needed to run this script, and despite my best attempts, occasional user input is required.

# setup configuration directory
CONFIG_DIR="/etc/rubberband"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "Creating rubberband configuration directory..."
    sudo mkdir $CONFIG_DIR
fi

sudo apt-get install curl python3-dev python-dev python-pip libblas-dev liblapack-dev libatlas-base-dev gfortran
sudo pip install virtualenv

# Java is a requirement of elasticsearch
java -version
status=$?
if [ $status -ne 0 ]; then
    echo "Installing Oracle JDK 8..."
    sudo add-apt-repository ppa:webupd8team/java
    sudo apt-get update
    sudo apt-get install oracle-java8-installer --quiet --assume-yes
fi

# Elasticsearch is installed as an upstart service on Ubuntu 16.04
echo "Checking elasticsearch status..."
sudo service elasticsearch status
status=$?
if [ $status -ne 0 ]; then
    echo "Installing elasticsearch..."
    wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
    echo "deb https://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list
    sudo apt-get update
    sudo apt-get install elasticsearch --quiet --assume-yes
fi

echo "Restarting elasticsearch..."
sudo service elasticsearch restart

echo "Installing python project requirements..."
root_dir="${PWD%/bin}"
virtualenv -p python3 "$root_dir/venv"
source "$root_dir/venv/bin/activate"
pip install -r "$root_dir/requirements-dev.txt"
pip install -e .

echo "Importing schema..."
$root_dir/rubberband-ctl create_index

echo "Populating elasticsearch..."
$root_dir/rubberband-ctl populate_index

git checkout $root_dir/tests/data

echo "Running tests..."
py.test $root_dir/tests/

echo "Creating files directory..."
mkdir $root_dir/files

echo "Done! Start the tornado server with `python server.py`"



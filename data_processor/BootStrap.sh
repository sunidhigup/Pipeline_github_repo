#!/bin/bash -xe
sudo pip3 install -U \
  boto3            \
  injector          \
  jsonschema     
   
sudo yum -y install gcc python-setuptools python-devel postgresql-devel
sudo pip3 install --upgrade pip
sudo /usr/local/bin/pip install psycopg2-binary
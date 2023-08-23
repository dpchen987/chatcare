#!/bin/bash


cd ../

# clean old build files
rm -rf build dist chatcare.egg-info chatcare/*\.c docker/chatcare-*-linux_x86_64.whl

# build
python setup.py bdist_wheel
cp dist/chatcare-*-linux_x86_64.whl docker

# clean build files
rm -rf build dist chatcare.egg-info chatcare/*\.c

# install local whl
#pip install --force-reinstall docker/chatcare-*-linux_x86_64.whl
#!/bin/bash


cd ../

# clean old build files
rm -rf build dist chatcare2.egg-info chatcare2/*\.c docker/chatcare2-*-linux_x86_64.whl

# build
python setup.py bdist_wheel
cp dist/chatcare2-*-linux_x86_64.whl docker

# clean build files
rm -rf build dist chatcare2.egg-info
find chatcare2/ -type f -name '*.c' -delete
# install local whl
#pip install --force-reinstall docker/chatcare2-*-linux_x86_64.whl

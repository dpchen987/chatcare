#!/usr/bin/env python3

fn = '../chatcare/__init__.py'
version = '0.1'
with open(fn) as f:
    for line in f:
        if '__version__' in line:
            version = line.split('=')[-1].strip().strip('\'"')
            break
print(version)

# change version in Dockfile
with open('Dockerfile') as f:
    lines = f.readlines()

old = 'chatcare-0.1-cp38-cp38-linux_x86_64.whl'
new = old.replace('0.1', version)
with open('Dockerfile', 'w') as f:
    for line in lines:
        newline = line.replace(old, new)
        f.write(newline)
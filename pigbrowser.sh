#!/bin/bash

# small utility script that keeps pigbrowser going.

# configure:
# path to pigbrowser folder that contains this script and src/ folder
PB_DIR=""
# python version
PYTHON="/usr/bin/python2.7"

export PYTHONPATH="${PB_DIR}/src:$PYTHONPATH"

until ${PYTHON} "${PB_DIR}/src/pb.py" ; do
	echo "{PB_DIR}/src/pb.py stopped.. Restarting.."
	sleep 1
done

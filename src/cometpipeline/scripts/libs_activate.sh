#! /usr/bin/bash

export CONDALIBS=$CONDA_PREFIX/../py27libs/lib/python2.7
export PYTHONPATH_OLD=$PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$CONDALIBS/site-packages

#! /usr/bin/bash

export CONDALIBS=$CONDA_PREFIX/../py37libs/lib/python3.7
export PYTHONPATH_OLD=$PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$CONDALIBS/site-packages

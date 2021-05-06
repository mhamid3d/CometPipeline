#! /usr/bin/env python


import os
import argparse
import sys
import mongorm


if not os.getenv("SHOW"):
	print("Please set a show first using 'cshow <show>'")
	sys.exit()


def all_shots():
	handler = mongorm.getHandler()
	filt = mongorm.getFilter()
	filt.search(handler['entity'], type__ne="asset", job=os.getenv('SHOW'))
	all_shots = handler['entity'].all(filt)
	if not all_shots:
		print("Could not find any shots in job: {}".format(os.getenv("SHOW")))
		sys.exit()
	return all_shots


def list_shots():
	for job in [x.get('label') for x in all_shots()]:
		print("-- {}".format(job))


parser = argparse.ArgumentParser(description='Set Comet Pipeline Shot')
parser.add_argument('-l', '--list', default=False, action='store_true', help='List all available shots')


kargs = parser.parse_known_args()
if kargs[0].list:
	list_shots()
	sys.exit()
else:
	parser.add_argument('Shot', metavar='shot', type=str, help='Name of shot')
	args = parser.parse_args()

targetShot = args.Shot


if not targetShot in [x.get('label') for x in all_shots()]:
	print("Please select a valid Shot:")
	list_shots()
	sys.exit()


confDir = os.path.abspath('{}/.config/CometPipeline'.format(os.getenv('HOME')))

if not os.path.exists(confDir):
	os.mkdir(confDir)

showFile = os.path.abspath(os.path.join(confDir, '.SHOW'))
shotFile = os.path.abspath(os.path.join(confDir, '.SHOT'))

if not os.path.exists(showFile):
	open(showFile, 'a').close()

if not os.path.exists(shotFile):
	open(shotFile, 'a').close()


# Write to file

with open(shotFile, "w") as f:
	f.write(targetShot)
	
sys.exit(99)

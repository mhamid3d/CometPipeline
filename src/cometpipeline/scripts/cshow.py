#! /usr/bin/env python


import os
import argparse
import sys
import mongorm


def all_jobs():
	handler = mongorm.getHandler()
	filt = mongorm.getFilter()
	filt.search(handler['job'])
	all_jobs = handler['job'].all(filt)
	return all_jobs


def list_shows():
	for job in [x.get('label') for x in all_jobs()]:
		print("-- {}".format(job))


parser = argparse.ArgumentParser(description='Set Comet Pipeline Show')
parser.add_argument('-l', '--list', default=False, action='store_true', help='List all available shows')


kargs = parser.parse_known_args()
if kargs[0].list:
	list_shows()
	sys.exit()
else:
	parser.add_argument('Show', metavar='show', type=str, help='Name of show')
	args = parser.parse_args()

targetShow = args.Show


if not targetShow in [x.get('label') for x in all_jobs()]:
	print("Please select a valid Job:")
	list_shows()
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

with open(showFile, "w") as f:
	f.write(targetShow)
	
sys.exit(99)

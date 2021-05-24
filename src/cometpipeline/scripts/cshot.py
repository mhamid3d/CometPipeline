#! /usr/bin/env python


import argparse
import sys
import mongorm
import time
import tempfile
from cometqt.util import get_settings

handler = mongorm.getHandler()
filt = mongorm.getFilter()
settings = get_settings(appName="PipeCore")


##### PARSE ARGS
parser = argparse.ArgumentParser(description='Set Comet Pipeline Show')
# parser.add_argument('-l', '--list', default=False, action='store_true', help='List all available shows')
parser.add_argument('-s', '--shell', default=False, action='store_true', help='Set environment only to shell')
parser.add_argument('-r', '--reload', default=False, action='store_true', help='Read environment file and reload')

kargs = parser.parse_known_args()

if kargs[0].reload:
    show = settings.value("shell/SHOW")
    shot = settings.value("shell/SHOT")

    if show and shot:
        SHOTPATH = "{}/{}".format(show, shot)
    else:
        sys.exit()

else:
    parser.add_argument('Shot', metavar='shot', type=str, help='<show>/<shot>')
    args = parser.parse_args()
    SHOTPATH = args.Shot


def dataObjectFromShotPath(shotPath):

    if "/" not in shotPath:
        show = shotPath
        shot = "root"
    else:
        show, shot = shotPath.split("/")

    if not show or not shot:
        print("Invalid job/shot", file=sys.stderr)
        sys.exit()

    filt.search(handler['job'], label=show)
    jobObject = handler['job'].one(filt)
    filt.clear()

    if not jobObject:
        print("Could not find job: {}".format(show), file=sys.stderr)
        sys.exit()

    filt.search(handler['entity'], label=shot, job=jobObject.label)
    entityObject = handler['entity'].one(filt)
    filt.clear()

    if not entityObject:
        print("Could not find shot: {}".format(shot), file=sys.stderr)
        sys.exit()

    return jobObject, entityObject


def getEnvVars(jobObject, entityObject):

    env_vars = {
        'SHOW': jobObject.label,
        'SHOT': entityObject.label,
        'SHOT_START': entityObject.get("framerange")[0],
        'SHOT_END': entityObject.get("framerange")[1],
        'OCIO': jobObject.ocioConfigFile(),
        'SHOW_RESOLUTION': '"{}"'.format(" ".join([str(x) for x in jobObject.get("resolution")]))
    }

    return env_vars


def writeToSettings(envVars):
    settings.beginGroup("shell")
    for k, v in envVars.items():
        settings.setValue(k, v)
    settings.endGroup()

    # TODO: this works on Linux, need to find a windows solution
    print(";".join(["export {}={}".format(k, v) for k, v in envVars.items()]))


def doParseAndSet(shotpath):
    t = time.time()
    JOBOBJECT, ENTITYOBJECT = dataObjectFromShotPath(shotpath)
    writeToSettings(envVars=getEnvVars(JOBOBJECT, ENTITYOBJECT))


doParseAndSet(SHOTPATH)
sys.exit(99)

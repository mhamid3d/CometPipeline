import os
from uuid import getnode
import platform


def getClientIdentifier():
    # Mac Addresss and Hostname separated by '-'
    return "{}-{}".format(':'.join(("%012X" % getnode())[i:i + 2] for i in range(0, 12, 2)),
                          platform.node())


def getCurrentUser():
    from cometqt.util import get_settings
    import mongorm

    settings = get_settings()

    username = settings.value("login/username")
    password = settings.value("login/password")
    email = settings.value("login/email")

    if username and password:
        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['user'], username=username, password=password, email=email)
        user_object = handler['user'].one(filt)

        if user_object:
            return user_object

    raise KeyError("Could not find a valid user")


def get_comet_job_root():
    return os.path.expandvars(os.getenv("COMET_JOB_ROOT"))


def get_abs_job_path(relative_path):
    return os.path.abspath(os.path.join(get_comet_job_root(), relative_path.strip("/")))


def user_in_crewType(userObject, jobObject, crewType=''):
    if not crewType or not crewType in jobObject.crew:
        raise RuntimeError("Invalid crew type: {}".format(crewType))
    return userObject.getUuid() in jobObject.crew[crewType]


def is_user_admin(userObject, jobObject):
    return userObject.getUuid() in jobObject.crew['Admins']
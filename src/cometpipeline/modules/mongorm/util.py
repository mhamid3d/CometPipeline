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

    raise KeyError, "Could not find a valid user"

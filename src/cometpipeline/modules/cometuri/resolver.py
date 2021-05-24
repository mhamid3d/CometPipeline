from urllib import parse
import os
import mongorm


class Resolver(object):

    _instance = False

    def __init__(self):
        self.cache = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Resolver, cls).__new__(cls, *args, **kwargs)

        return cls._instance


def clean_uri(uri):
    uri = uri.strip("{").strip("}")
    if "comet:/" in uri or "comet://" in uri:
        uri = uri.replace("comet://", "comet:")
        uri = uri.replace("comet:/", "comet:")

    return uri


def uri_to_fields(uri):
    uri = clean_uri(uri)

    parsed = parse.urlparse(uri)
    query = parsed.query

    query_tokens = query.split('&')
    fields = {}

    for field in query_tokens:
        key, value = field.split('=')
        # TODO: should we check if its a float as well?
        if value.isnumeric():
            value = int(value)
        fields[key] = value

    return fields


def uri_to_object(uri):

    uri = clean_uri(uri)

    parsed = parse.urlparse(uri)
    path = parsed.path
    query = parsed.query

    job = os.getenv("SHOW")

    split_path = path.split("/")
    if len(split_path) > 2:
        return None
    elif len(split_path) == 1:
        package_string = split_path[0]
    elif len(split_path) == 2:
        package_string = split_path[-1]
        job = split_path[0]

    packageLabel = os.path.expandvars(package_string)

    query_tokens = query.split('&')
    fields = {}

    for field in query_tokens:
        key, value = field.split('=')
        # TODO: should we check if its a float as well?
        if value.isnumeric():
            value = int(value)
        fields[key] = value

    db = mongorm.getHandler()
    flt = mongorm.getFilter()

    flt.search(db['package'], label=packageLabel, job=job)

    packageObject = db['package'].one(flt)

    if not packageObject:
        return None

    versionObject = packageObject.latest(version=None if not 'v' in fields else fields['v'])

    if not versionObject:
        return None

    if 'c' in fields:
        contents = versionObject.children()
        if not contents:
            return None
        contentObject = versionObject.default_content()
        for content in contents:
            if fields['c'] == content.get("label"):
                contentObject = content

        return contentObject

    return versionObject


def uri_to_filepath(uri):
    pass
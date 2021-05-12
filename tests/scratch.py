import os
from urllib import parse
import mongorm

uri = "{comet:/dlr/bre330/model_prop_walkman_varA_lod_hi?v=approved}"
uri = "{comet:/833e050c-458e-48a9-bfd9-87eac175ec65?v=approved}"
uri = "{comet:dlr/model_${SHOT}_varA_lod_hi?v=34}"


def clean_uri(uri):
    uri = uri.strip("{").strip("}")
    if "comet:/" in uri or "comet://" in uri:
        uri = uri.replace("comet://", "comet:")
        uri = uri.replace("comet:/", "comet:")

    return uri


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

    versions = packageObject.children()

    if not versions:
        return None

    versions.sort("version", reverse=True)

    versionObject = versions[0]

    if 'v' in fields:
        versionToken = fields['v']

        if versionToken.isdigit():
            for version in versions:
                if version.get("version") == versionToken:
                    versionObject = version
        elif versionToken == "approved":
            for version in versions:
                if version.get("status") == "approved":
                    versionObject = version
        elif versionToken == "declined":
            for version in versions:
                if version.get("status") == "declined":
                    versionObject = version
        elif versionToken == "pending":
            for version in versions:
                if version.get("status") == "pending":
                    versionObject = version

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


uri_to_object(uri)

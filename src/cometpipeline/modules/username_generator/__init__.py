import mongorm


def generate_username(firstname, lastname):

    if not firstname or not lastname:
        raise ValueError("Please provide a valid first and last name")

    # Try with default
    firstname = firstname.lower()
    lastname = lastname.lower()
    username = "{}{}".format(firstname[0], lastname)

    db = mongorm.getHandler()
    flt = mongorm.getFilter()
    flt.search(db['user'])
    existingUsers = db['user'].all(flt)

    existingUsernames = [x.get("username") for x in existingUsers]

    if username in existingUsernames:
        firstIdx = 1
        while firstIdx <= len(firstname) and username in existingUsernames:
            username = "{}{}".format(firstname[0:firstIdx], lastname)
            firstIdx += 1

    return username

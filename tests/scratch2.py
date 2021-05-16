import mongorm


db = mongorm.getHandler()
flt = mongorm.getFilter()

flt.search(db['job'])

job = db['job'].one(flt)
cr = job.crew_dict()
cr['Creator'] = ["dd06facb-03b3-4bf6-8fa3-d264b427deb8"]
cr['Admins'] = ["dd06facb-03b3-4bf6-8fa3-d264b427deb8"]
job.crew = cr
job.save()
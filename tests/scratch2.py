import mongorm


db = mongorm.getHandler()
flt = mongorm.getFilter()

flt.search(db['entity'])

job = db['entity'].one(flt)
job.framerange = [1001, 1101]
print(type(job.framerange))
job.save()

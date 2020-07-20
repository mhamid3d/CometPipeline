from mongorm import interfaces
import mongorm
import datetime

dh = mongorm.getHandler()

# job = Job()
# job._generate_id()
# job.path = "C:/jobs/CAIN"
# job.label = "CAIN"
# job.created = datetime.datetime.now()
# job.modified = datetime.datetime.now()
# job.job = job.label
# job.fullname = "Garbage Truck"
# job.resolution = [1920, 1080]
# job.created_by = "mham"
# job.thumbnail = "C:/jobs/CAIN/config/thumb.png"
#
# job.save()

entity = interfaces.Entity()
entity._generate_id()
entity.prefix = "prop"
entity.label = "knife"
entity.created = datetime.datetime.now()
entity.modified = datetime.datetime.now()
entity.created_by = "mham"
entity.job = "CAIN"
entity.thumbnail = "C:/jobs/CAIN/assets/Character/ellie/thumb.png"
entity.type = "asset"
entity.production = True
entity.parent_uuid = "8b1b65a2-eb99-470a-afa1-c0fa6bf2acdb"
entity.framerange = []
entity.path = "C:/jobs/CAIN/assets/{0}/{1}".format(entity.prefix, entity.label)


entity.save()
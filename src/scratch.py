import mongorm


handler = mongorm.getHandler()
filter = mongorm.getFilter()

filter.search(handler['entity'])

all = handler['entity'].all(filter)

for x in all:
    x.delete()
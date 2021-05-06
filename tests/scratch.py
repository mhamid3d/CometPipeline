import mongorm

db = mongorm.getHandler()
nott = db['notification'].create(
    receiver_uuid="fc766aab-ff65-4f7e-9c40-af3cb8c62b18",
    description="Hello. This is a NOT!!!"
)

nott.save()
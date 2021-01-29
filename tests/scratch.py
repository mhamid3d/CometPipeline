import mongorm

db = mongorm.getHandler()
file1 = db['content'].create(
    parent_uuid="d393a5f0-b18e-4d5f-92c7-f5df5e062a54",
    format="ma:maya_ascii",
    label="main",
    job="DELOREAN",
    path="/jobs/DELOREAN/production/ab_seq/_publish/APKG/APKG_ab_seq_anim_lod100/APKG_ab_seq_anim_lod100_v001/main.ma"
)
file2 = db['content'].create(
    parent_uuid="d393a5f0-b18e-4d5f-92c7-f5df5e062a54",
    format="xml:xml",
    label="pkg",
    job="DELOREAN",
    path="/jobs/DELOREAN/production/ab_seq/_publish/APKG/APKG_ab_seq_anim_lod100/APKG_ab_seq_anim_lod100_v001/pkg.xml"
)
file1.save()
file2.save()
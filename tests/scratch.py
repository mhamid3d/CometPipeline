import os, sys
import yaml

filePath = "/home/mhamid/Downloads/Material Manager v5.2.0/mm_material_presets.txt"
yamlFile = "/home/mhamid/_dev/CometPipeline-DCC/cometmaya/shelf_scripts/materialTagConfig.yaml"

with open(yamlFile) as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

with open(yamlFile, "w") as f:
    data['presets']['barnicle'] = {'color': [0.2, 0.4, 0.5]}
    yaml.dump(data, f)
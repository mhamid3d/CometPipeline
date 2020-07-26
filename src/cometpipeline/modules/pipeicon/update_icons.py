import subprocess
import os

IMG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "icons"))
ICON_PATHS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "icon_paths.py"))
QRC_FILE = os.path.abspath(os.path.join(IMG_PATH, "icons.qrc"))
RCC_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "icons_rcc.py"))


# This section for updating the variables list
img_list = []
for img in os.listdir(IMG_PATH):
    if img.endswith("qrc"):
        continue
    img_name = os.path.splitext(img)[0]
    img_list.append((img, "{} = ':/pipeicon/{}'".format(img_name, img)))

img_list = sorted(img_list)

# write qrc file
qrc_file = open(QRC_FILE, "w")
qrc_file.write("<RCC>\n")
qrc_file.write('  <qresource prefix="pipeicon">\n')
for qrc_obj in img_list:
    qrc_string = "    <file>{}</file>\n".format(qrc_obj[0])
    qrc_file.write(qrc_string)
qrc_file.write("  </qresource>\n")
qrc_file.write("</RCC>\n")
qrc_file.close()

# write rcc file
subprocess.call('pyside2-rcc {} -o {}'.format(QRC_FILE, RCC_FILE), shell=True)
rcc_file = open(RCC_FILE, "rt")
rcc_text = rcc_file.readlines()
rcc_file.close()
rcc_file = open(RCC_FILE, "w")
for line in rcc_text:
    rcc_file.write(line.replace("from PySide2", "from qtpy"))
rcc_file.close()

# write icon_paths file
ip_file = open(ICON_PATHS_FILE, "w")
ip_file.write("from pipeicon import icons_rcc"+'\n'+'\n'+'\n')
for qrc_obj in img_list:
    ip_file.write(qrc_obj[1]+'\n')

ip_file.close()

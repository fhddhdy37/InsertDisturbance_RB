#%%
from lxml import etree as ET
import xmlschema
from scenariogeneration import xosc
from pathlib import Path
import os

file_path = Path(__file__).resolve()
src_dir = file_path.parent / "src"

output_path = src_dir / "out/test.xosc"

input_file = "esmini/straight_500m.xosc"
input_path = src_dir / input_file

disturbance_file = "rain.xosc"
disturbance_path = src_dir / disturbance_file

xsd_file = src_dir / "xsd/OpenSCENARIO-1.2.xsd"
schema = xmlschema.XMLSchema(xsd_file)

in_tree = ET.parse(input_path)
in_root = in_tree.getroot()

dis_tree = ET.parse(disturbance_path)
dis_root = dis_tree.getroot()

#%%
elem = ".//StopTrigger"
print(f"find {elem}")
for e in list(map(xmlschema.XsdElement.get_parent_type, schema.findall(elem))):
    print(e.name)
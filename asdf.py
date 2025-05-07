def find_child(parent):
    for child in parent:
        print(child.tag)
        find_child(child)

RULE = {
    "ScenarioObject": "Entities",
    "Private": "Actions",
    "GlobalAction": "Actions",
    "ManeuverGroup": "Act",
}

from pathlib import Path
from lxml import etree as ET
import xmlschema
import os

from scenariogeneration import xosc, xodr, esmini

file_path = Path(__file__).resolve()
src_dir = file_path.parent / "src"

output_path = src_dir / "out/invalid.xosc"

input_file = "esmini/straight_500m.xosc"
input_path = src_dir / input_file

disturbance_file = "invalid_dist.xosc"
disturbance_path = src_dir / disturbance_file

in_tree = ET.parse(input_path)
in_root = in_tree.getroot()

dis_tree = ET.parse(disturbance_path)
dis_root = dis_tree.getroot()

for child in dis_root:
    try:
        elem = in_root.find(f".//{RULE[child.tag]}/{child.tag}")
        elem.getparent().append(child)
    except KeyError:
        pass

ET.indent(in_root, space="  ")
in_tree.write(output_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
print(f"Output written to {output_path}")

try:
    sce = xosc.ParseOpenScenario(output_path)
    esmini(sce, os.path.join('D:\\TUK\\AILAB\\opensources\\esmini-demo'))
except:
    print("Invalid .xosc file")
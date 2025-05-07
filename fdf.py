import os
from pathlib import Path
from lxml import etree as ET

from scenariogeneration import esmini, xosc, xodr, Scenario

file_path = Path(__file__).resolve()
src_dir = file_path.parent / "src"

output_path = src_dir / "out/test.xosc"

input_file = "esmini/straight_500m.xosc"
input_path = src_dir / input_file

disturbance_file = "fallOBJ.xosc"
disturbance_path = src_dir / disturbance_file

sce = xosc.ParseOpenScenario(input_path)
dis = ET.parse(disturbance_path).getroot()

for child in dis:
    

esmini(sce,os.path.join('D:\\TUK\\AILAB\\opensources\\esmini-demo'))
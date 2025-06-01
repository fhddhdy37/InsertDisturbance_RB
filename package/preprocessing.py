from lxml import etree as ET
from typing import Literal
from pydantic import BaseModel

from .config import TARGETS

def get_names(fp):
    tree = ET.parse(fp)
    root = tree.getroot()
    name_dict = {}

    for target in TARGETS.__args__:
        for elem in root.findall(f".//{target}"):
            if name := elem.attrib.get("name"):
                name_dict[name] = elem.tag
    names = tuple(name_dict.keys())
    class d:
        d =''

    return d

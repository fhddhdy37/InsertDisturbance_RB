from typing import Literal

from lxml import etree as ET
from pydantic import create_model

from GD import config as cf

def preprocessing():
    tree = ET.parse(cf.INPUT_PATH)
    root = tree.getroot()
    names = ["None"]

    for target in cf.TARGETS.__args__:
        for elem in root.findall(f".//{target}"):
            if name := elem.attrib.get("name"):
                names.append(name)
    cf.NAMES = Literal[tuple(names)]

    metaDataRuntime = create_model(
        "MetaData",
        type=cf.TYPES,
        target=cf.TARGETS,
        name=cf.NAMES,
        code=str
    )
    responseFormatRuntime = create_model(
        "ResponseData",
        data=list[metaDataRuntime]
    )
    cf.MetaData = metaDataRuntime
    cf.ResponseData = responseFormatRuntime

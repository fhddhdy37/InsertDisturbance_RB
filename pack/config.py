from pathlib import Path
import os
from typing import Literal
from pydantic import BaseModel

# path related setting
INPUT_FILE = ""
INPUT_DIR = ""
OUTPUT_FILE = ""

FILE_PATH = Path(__file__).resolve()
SRC_DIR = FILE_PATH.parent.parent / "src"
DIST_DIR = SRC_DIR / "disturbance"
TMP_DIR = DIST_DIR / "tmp"

if not TMP_DIR.is_dir():
    os.mkdir(TMP_DIR)

XSD_FILE = SRC_DIR / "xsd" / "OpenSCENARIO-1.2.xsd"

# model related setting
TYPES = Literal["ScenarioObject", "Private", "ManeuverGroup"]
TARGETS = Literal["Entities", "Init", "Act"]
NAMES = None

class MetaData(BaseModel):
    type: TYPES
    target: TARGETS
    name: str
    code: str

class ResponseData(BaseModel):
    data: list[MetaData]


# personal setting

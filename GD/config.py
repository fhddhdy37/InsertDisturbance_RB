from pathlib import Path
import os
from typing import Literal
from pydantic import BaseModel

# path related setting
TIME = ""

INPUT_PATH = ""
INPUT_DIR = ""
OUTPUT_PATH = ""

BASE_PATH = Path(__file__).resolve()
SRC_DIR = BASE_PATH.parent.parent / "src"
DIST_DIR = SRC_DIR / "disturbance"
TMP_DIR = DIST_DIR / "tmp"
GENERATION_DIR = SRC_DIR / "generated"

if not TMP_DIR.is_dir():
    os.mkdir(TMP_DIR)
if not GENERATION_DIR.is_dir():
    os.mkdir(GENERATION_DIR)

XSD_PATH = SRC_DIR / "xsd" / "OpenSCENARIO-1.2.xsd"

# model related setting
RULE = {
    "ScenarioObject": "Entities",
    "GlobalAction": "Actions",
    "Private": "Actions",
    "ManeuverGroup": "Act",
}

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
GPT_API = "your gpt api key"
GEMINI_API = "your gemini api key"
ESMINI_PATH = Path("your esmini path")


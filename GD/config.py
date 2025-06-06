import os
from typing import Literal
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel

# path related config
INPUT_PATH = ""
INPUT_DIR = ""
OUTPUT_PATH = ""

BASE_PATH = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_PATH / "src"
DIST_DIR = SRC_DIR / "disturbance"
TMP_DIR = DIST_DIR / "tmp"
GENERATION_DIR = SRC_DIR / "generated"

if not TMP_DIR.is_dir():
    os.mkdir(TMP_DIR)
if not GENERATION_DIR.is_dir():
    os.mkdir(GENERATION_DIR)

XSD_PATH = SRC_DIR / "xsd" / "OpenSCENARIO-1.2.xsd"

# experiment related config
DATE = datetime.now().strftime("%Y%m%d_%H%M%S")

LOG_BASE = SRC_DIR / "logs"
LOG_DIR = LOG_BASE / DATE
if not LOG_BASE.is_dir():
    os.mkdir(LOG_BASE)
if not LOG_DIR.is_dir():
    os.mkdir(LOG_DIR)

# model related config
TYPES = Literal["ScenarioObject", "Private", "GlobalAction", "ManeuverGroup"]
TARGETS = Literal["Entities", "Actions", "Act"]
NAMES = None

class MetaData(BaseModel):
    type: TYPES
    target: TARGETS
    name: str
    code: str

class ResponseData(BaseModel):
    data: list[MetaData]


# personal config
GPT_API = "your gpt api key"
GEMINI_API = "your gemini api key"
ESMINI_PATH = Path("your esmini path")

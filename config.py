from pathlib import Path

RULE = {
    "ScenarioObject": "Entities",
    "Private": "Actions",
    "GlobalAction": "Actions",
    "ManeuverGroup": "Act",
}

FILE_PATH = Path(__file__).resolve()
SRC_DIR = FILE_PATH.parent / "src"
XSD_FILE = SRC_DIR / "xsd/OpenSCENARIO-1.2.xsd"

GPT_API = "your gpt api key"
GEMINI_API = "your gemini api key"
ESMINI_PATH = Path("your esmini dir")
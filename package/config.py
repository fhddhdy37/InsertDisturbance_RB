from pathlib import Path
import os

RULE = {
    "ScenarioObject": "Entities",
    "Private": "Actions",
    "GlobalAction": "Actions",
    "ManeuverGroup": "Act",
}

SIM_NAME = "esmini" # or "carla" or etc.

FILE_PATH = Path(__file__).resolve()
SRC_DIR = FILE_PATH.parent.parent / "src"
SCENE_DIR = SRC_DIR / SIM_NAME
DIST_DIR = SRC_DIR / "disturbance"
OUT_DIR = SCENE_DIR / "out"
TMP_DIR = DIST_DIR / "tmp"

if not OUT_DIR.is_dir():
    os.mkdir(OUT_DIR)
if not TMP_DIR.is_dir():
    os.mkdir(TMP_DIR)

XSD_FILE = SRC_DIR / "xsd" / "OpenSCENARIO-1.2.xsd"


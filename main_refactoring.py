from pack import config as cf
from pack.preprocessing import preprocessing

from pathlib import Path
from datetime import datetime

mode = "gemini"
model = "gemini-2.5-flash-preview-05-20"

cf.INPUT_FILE = Path(r"D:\TUK\25-1\BusinessAnalatics\InsertDisturbance_RB\src\esmini\straight_500m.xosc").resolve()
cf.INPUT_DIR = cf.INPUT_FILE.parent
output_file = f"gen_scenario_{datetime.now().strftime("%y%m%d%H%M%S")}.xosc"
cf.OUTPUT_FILE = cf.INPUT_DIR / output_file

preprocessing()

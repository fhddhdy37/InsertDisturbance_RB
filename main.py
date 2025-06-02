from GD import config as cf
from GD.controller import GPTController, GeminiController
from GD.preprocessing import preprocessing

from scenariogeneration import xosc, esmini

from pathlib import Path
from datetime import datetime
import traceback

if __name__ == "__main__":
    cf.TIME = datetime.now().strftime("%y%m%d%H%M%S")

    mode = "gemini"
    model = "gemini-2.5-flash-preview-05-20"
    # mode = "gpt"
    # model = "gpt-4.1-nano"

    input_file = "your scenario file path"
    output_file = f"gen_scenario_{cf.TIME}.xosc"
    input_text = "전방 100m에 낙석 발생"
    
    cf.INPUT_PATH = Path(input_file).resolve()
    cf.INPUT_DIR = cf.INPUT_PATH.parent
    cf.OUTPUT_PATH = cf.INPUT_DIR / output_file

    preprocessing()

    if mode == "gpt":
        controller = GPTController()
    elif mode == "gemini":
        controller = GeminiController()
    else:
        raise ValueError("mode is supported only \"gemini\" or \"gpt\"")        
    
    while controller.response_count < 20:
        print(controller.response_count)
        controller.gen_disturbance(input_text, model, "fs")
        controller.insert_scenario()

        try:
            sce = xosc.ParseOpenScenario(controller.output_path)
        except Exception as e:
            controller.err = traceback.format_exc()
            continue
        else:
            esmini(sce, cf.ESMINI_PATH, generation_path=cf.GENERATION_DIR)
            break
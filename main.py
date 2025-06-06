from pathlib import Path
import traceback

from scenariogeneration import xosc

from GD import esmini
from GD import config as cf
from GD.controller import GPTController, GeminiController
from GD.preprocessing import preprocessing

if __name__ == "__main__":
    mode = "gemini"
    model = "gemini-2.5-flash-preview-05-20"

    input_file = "your scenario file path"
    output_file = f"gen_scenario_{cf.DATE}.xosc"
    input_text = "중앙선 넘어 반대 차선에서 차량이 주행하는 상황"
    prompting = ("fs", )

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
    
    controller.gen_disturbance(input_text, model, *prompting)

    try:
        sce = xosc.ParseOpenScenario(controller.output_path)
    except Exception as e:
        print(traceback.format_exc())
    else:
        esmini(sce, cf.ESMINI_PATH, generation_path=cf.GENERATION_DIR)

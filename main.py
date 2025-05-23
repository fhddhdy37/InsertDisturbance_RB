from package import *
from package.gpt_controller import GPTController
from package.gemini_controller import GeminiController

from scenariogeneration import xosc, esmini

if __name__ == "__main__":
    mode = "gpt"     # or "gpt"

    input_file = "straight_500m.xosc"       # 입력 시나리오 파일명
    output_file = "in_test.xosc"            # 최종 출력 시나리오 파일명
    input_text = "전방 100m 보행자 무단횡단"       # 외란 상황에 따라 다르게 입력

    if mode == "gpt":
        controller = GPTController(input_file, output_file, "cot")
    elif mode == "gemini":
        controller = GeminiController(input_file, output_file, "cot")
    else:
        raise ValueError("mode is supported only \"gemini\" or \"gpt\"")
    controller.gen_disturbance(input_text)
    controller.insert_scenario()

    if controller.is_valid():
        sce = xosc.ParseOpenScenario(controller.output_path)
        esmini(sce, ESMINI_PATH, generation_path=OUT_DIR)
    else:
        print("Invalid .xosc file")
from package import *
from package.gpt_controller import GPTController
from package.gemini_controller import GeminiController

from scenariogeneration import xosc, esmini

if __name__ == "__main__":
    mode = "gemini"             # or "gpt"
    model = "gemini-2.5-flash-preview-05-20"  # "gpt-4.1-nano" or etc.

    input_file = "straight_500m.xosc"       # 입력 시나리오 파일명
    output_file = "in_test.xosc"            # 최종 출력 시나리오 파일명
    input_text = "전방 100m 보행자 무단횡단"       # 외란 상황에 따라 다르게 입력
    response_count = 1

    if mode == "gpt":
        controller = GPTController(input_file, output_file, "fs", "cot")
    elif mode == "gemini":
        controller = GeminiController(input_file, output_file, "fs", "cot")
    else:
        raise ValueError("mode is supported only \"gemini\" or \"gpt\"")
    
    while True:
        controller.gen_disturbance(input_text, model)
        controller.insert_scenario()

        if controller.is_valid():
            sce = xosc.ParseOpenScenario(controller.output_path)
            esmini(sce, ESMINI_PATH, generation_path=OUT_DIR)
            break
        break
        response_count += 1
        
        
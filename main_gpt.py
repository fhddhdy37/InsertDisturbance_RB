from config import *
from prompts import SYS_PROMPT
from openai import OpenAI
from controller import Controller, ResponseData

class GPTController(Controller):
    def __init__(self, input_file, disturbance_file, output_file, *args):
        super().__init__(input_file, disturbance_file, output_file, *args)
        self.client = OpenAI(api_key=GPT_API)

    def gen_disturbance(self, input_text):
        """
        LLM으로부터 자연어 입력을 코드 조각으로 생성하는 함수

        프롬프트 상세 설명:
            user 프롬프트의 content에 프롬프팅 기법과 외란 상황, 입력 시나리오를 제공하여 코드 조각 생성 유도
            코드 31번 줄 참고
        """

        response = self.client.responses.parse(
            model="gpt-4.1-nano",
            text_format=ResponseData,
            input=[
                {
                    "role": "system", 
                    "content": SYS_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
                                {self.user_prompt}

                                질문: {input_text}
                                base scenario:
                                {self.base_scenario}
                                """
                }
            ]
        )
        
        print(response.output_parsed)
        response_parsed = response.output_parsed.data
        
        self._write_disturbance(response_parsed)

if __name__ == "__main__":
    input_file = "esmini/straight_500m.xosc"    # 입력 시나리오 파일명
    disturbance_file = "gpt_d.xosc"             # LLM을 통해 출력될 시나리오 파일명
    output_file = "out/in_test.xosc"            # 최종 출력 시나리오 파일명
    input_text = "전방 100m 낙석 상황"           # 외란 상황에 따라 다르게 입력

    controller = GPTController(input_file, disturbance_file, output_file, "cot")
    controller.gen_disturbance(input_text)
    controller.insert_scenario()

    if controller.is_valid():
        from scenariogeneration import xosc, esmini
        sce = xosc.ParseOpenScenario(controller.output_path)
        esmini(sce, ESMINI_PATH)
    else:
        print("Invalid .xosc file")
from config import *
from prompts import SYS_PROMPT
from openai import OpenAI
import re
from controller import Controller, ResponseData

class GeminiController(Controller):
    def __init__(self, input_file, disturbance_file, output_file, *args):
        super().__init__(input_file, disturbance_file, output_file, *args)
        self.client = OpenAI(
            api_key=GEMINI_API,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

    def gen_disturbance(self, input_text):
        """
        LLM으로부터 자연어 입력을 코드 조각으로 생성하는 함수

        프롬프트 상세 설명:
            user 프롬프트의 content에 프롬프팅 기법과 외란 상황, 입력 시나리오를 제공하여 코드 조각 생성 유도
            코드 35번 줄 참고
        """

        response = self.client.beta.chat.completions.parse(
            model="gemini-2.0-flash",
            response_format=ResponseData,
            messages=[
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

        print(response.choices[0].message.parsed)
        response_parsed = response.choices[0].message.parsed.data
        
        self._write_disturbance(response_parsed)

    def _extract_xml_blocks(self, text):
        # decrepted
        return
        """
        주어진 text에서 ``` ... ``` 로 감싸진 블록의 내용만 추출하여
        리스트로 반환합니다.
        """
        pattern = re.compile(r'```\s*(.*?)```', re.DOTALL)
        blocks = pattern.findall(text)

        code_slice = "<OpenSCENARIO>\n"
        for block in blocks:
            code_slice += "\n".join(block.strip().split('\n')[1:])
        code_slice += "\n</OpenSCENARIO>"

        return code_slice

if __name__ == "__main__":
    input_file = "esmini/straight_500m.xosc"    # 입력 시나리오 파일명
    disturbance_file = "gpt_d.xosc"             # LLM을 통해 출력될 시나리오 파일명
    output_file = "out/in_test.xosc"            # 최종 출력 시나리오 파일명
    input_text = "전방 100m 낙석 상황"           # 외란 상황에 따라 다르게 입력

    controller = GeminiController(input_file, disturbance_file, output_file, "cot")
    controller.gen_disturbance(input_text)
    controller.insert_scenario()

    if controller.is_valid():
        from scenariogeneration import xosc, esmini
        sce = xosc.ParseOpenScenario(controller.output_path)
        esmini(sce, ESMINI_PATH)
    else:
        print("Invalid .xosc file")
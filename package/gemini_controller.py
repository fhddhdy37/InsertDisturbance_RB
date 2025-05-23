from package import *
from package.prompts import SYS_PROMPT
from package.controller import Controller, ResponseData

from openai import OpenAI

from datetime import datetime

class GeminiController(Controller):
    def __init__(self, input_file, output_file, *args):
        super().__init__(input_file, output_file, *args)
        self.disturbance_path = TMP_DIR / f"test_gemini_dist_{datetime.now().strftime("%y%m%d%H%M%S")}.xosc"
        self.client = OpenAI(
            api_key=GEMINI_API,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

    def gen_disturbance(self, input_text):
        """
        LLM으로부터 자연어 입력을 코드 조각으로 생성하는 함수

        프롬프트 상세 설명:
            user 프롬프트의 content에 프롬프팅 기법과 외란 상황, 입력 시나리오를 제공하여 코드 조각 생성 유도
            코드 36번 줄 참고
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

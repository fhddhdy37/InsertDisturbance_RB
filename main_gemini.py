from config import *
from prompts import PROMPT_SET, SYS_PROMPT
from openai import OpenAI
from lxml import etree as ET
import xmlschema
import re

class Controller:
    def __init__(self, input_file, disturbance_file, output_file, *args):
        """
        입/출력 자원을 효율적으로 관리하기 위해 클래스로 정의
        기본적인 경로 및 키값에 관한 세팅은 config.py에 정의
        시스템 프롬프트 및 프롬프팅 기법에 관한 세팅은 prompts.py에 정의

        input_path : 입력 시나리오의 경로
        disturbance_path : 생성된 외란 시나리오의 경로
        output_path : 최종 출력 시나리오의 경로
        schema : 검증을 위한 XML 스키마 객체

        in_tree : 입력 시나리오의 XMLElementTree 객체
        in_root : 입력 시나리오의 루트 XMLElement 객체, <OpenSCENARIO>
        dis_tree : 외란 시나리오의 XMLElementTree 객체
        dis_root : 외란 시나리오의 루트 XMLElement 객체, <OpenSCENARIO>

        client : OpenAI 클라이언트 객체
        user_prompt : user 프롬프트에서 적용할 프롬프팅 기법
        """

        self.input_path = SRC_DIR / input_file
        self.disturbance_path = SRC_DIR / disturbance_file
        self.output_path = SRC_DIR / output_file
        self.schema = xmlschema.XMLSchema(XSD_FILE)

        self.in_tree = ET.parse(self.input_path)
        self.in_root = self.in_tree.getroot()
        self.dis_tree = None
        self.dis_root = None

        self.client = None
        self.user_prompt = ""
        for arg in args:
            self.user_prompt += PROMPT_SET[arg.lower()]

    def gen_disturbance(self, input_text):
        """
        LLM으로부터 자연어 입력을 코드 조각으로 생성하는 함수

        프롬프트 상세 설명:
            user 프롬프트의 content에 프롬프팅 기법과 외란 상황, 입력 시나리오를 제공하여 코드 조각 생성 유도
            코드 82번 줄 참고

        코드 조각의 출력 파일 예시:
            <OpenSCENARIO>
            <ScenarioObject name="rock_1">
                ...
            </ScenarioObject>
            <Private entityRef="Ego">
                ...
            </Private>
            <ManeuverGroup name="MyManeuver">
                ...
            </ManeuverGroup>
            ...
            </OpenSCENARIO>
        """

        if self.client is None:
            self.client = OpenAI(
                api_key=GEMINI_API,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

        response = self.client.chat.completions.create(
            model="gemini-2.0-flash",
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
                                {ET.tostring(self.in_root).decode()}
                                """
                }
            ]
        )

        content = response.choices[0].message.content
        print(content)
        out_xosc = self._extract_xml_blocks(content)

        self.dis_root = ET.fromstring(out_xosc)
        self.dis_tree = ET.ElementTree(self.dis_root)

        ET.indent(self.dis_tree, "  ")
        self.dis_tree.write(self.disturbance_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
        print(f"Output written to {self.disturbance_path}")

    def insert_scenario(self):
        """
        LLM으로부터 생성한 외란 코드 조각을 입력 시나리오에 삽입
        """
        
        for child in self.dis_root:
            elem = self.in_root.find(f".//{RULE[child.tag]}/{child.tag}")
            if elem is not None:
                elem.getparent().append(child)
        
        ET.indent(self.in_root, space="  ")
        self.in_tree.write(self.output_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
        print(f"Output written to {self.output_path}")

    def _extract_xml_blocks(self, text):
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

    def is_valid(self):
        return self.schema.is_valid(self.output_path)

if __name__ == "__main__":
    input_file = "esmini/straight_500m.xosc"    # 입력 시나리오 파일명
    disturbance_file = "gpt_d.xosc"             # LLM을 통해 출력될 시나리오 파일명
    output_file = "out/in_test.xosc"            # 최종 출력 시나리오 파일명
    input_text = "전방 100m 낙석 상황"           # 외란 상황에 따라 다르게 입력

    controller = Controller(input_file, disturbance_file, output_file)
    controller.gen_disturbance(input_text)
    controller.insert_scenario()

    if controller.is_valid():
        from scenariogeneration import xosc, esmini
        sce = xosc.ParseOpenScenario(controller.output_path)
        esmini(sce, ESMINI_PATH)
    else:
        print("Invalid .xosc file")
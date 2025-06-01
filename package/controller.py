from package import *
from package.prompts import PROMPT_SET

from lxml import etree as ET
import xmlschema
import re
from pydantic import BaseModel

class MetaData(BaseModel):
    type: TYPES
    target: TARGETS
    name: str
    code: str

class ResponseData(BaseModel):
    data: list[MetaData]

class Controller:
    def __init__(self, input_file, output_file, *args):
        """
        입/출력 자원을 효율적으로 관리하기 위해 클래스로 정의
        기본적인 경로 및 키값에 관한 세팅은 `config.py`에 정의
        시스템 프롬프트 및 프롬프팅 기법에 관한 세팅은 `prompts.py`에 정의

        input_path : 입력 시나리오의 경로
        disturbance_path : 생성된 외란 시나리오의 경로
        output_path : 최종 출력 시나리오의 경로
        schema : 검증을 위한 XML 스키마 객체

        in_tree : 입력 시나리오의 XMLElementTree 객체
        in_root : 입력 시나리오의 루트 XMLElement 객체, <OpenSCENARIO>
        dis_tree : 외란 시나리오의 XMLElementTree 객체
        dis_root : 외란 시나리오의 루트 XMLElement 객체, <OpenSCENARIO>
        response_data : 

        client : OpenAI 클라이언트 객체
        user_prompt : user 프롬프트에서 적용할 프롬프팅 기법
        """

        self.input_path = SCENE_DIR / input_file
        self.disturbance_path = TMP_DIR / "test_disturbance.xosc"
        self.output_path = OUT_DIR / output_file
        self.schema = xmlschema.XMLSchema(XSD_FILE)

        self.in_tree = ET.parse(self.input_path)
        self.in_root = self.in_tree.getroot()
        self.base_scenario = ET.tostring(self.in_root).decode()
        self.dis_tree = None
        self.dis_root = None
        self.response_data = None

        self.client = None
        self.user_prompt = ""
        for arg in args:
            self.user_prompt += PROMPT_SET[arg.lower()]

    def gen_disturbance(self, input_text, model):
        """
        LLM으로부터 자연어 입력을 코드 조각으로 생성하는 함수

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
        pass

    def _write_disturbance(self, response_parsed):
        out_xosc = "<OpenSCENARIO>\n"
        for data in response_parsed:
            out_xosc += data.code
            print(f"type: {data.type}, target: {data.target}, name: {data.name}")
        out_xosc += "\n</OpenSCENARIO>"

        self.dis_root = ET.fromstring(out_xosc)
        self.dis_tree = ET.ElementTree(self.dis_root)

        ET.indent(self.dis_tree, "  ")
        self.dis_tree.write(self.disturbance_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
        print(f"Disturbance file written to {self.disturbance_path}")

    def insert_scenario(self):
        """
        LLM으로부터 생성한 외란 코드 조각을 입력 시나리오에 삽입
        """
        
        for child in self.dis_root:
            try:
                elem = self.in_root.find(f".//{RULE[child.tag]}/{child.tag}")
            except KeyError:
                elem = self.in_root.find(f".//{child.tag}")

            if elem is not None:
                elem.getparent().append(child)

        # for item in self.response_data:
        #     item.target
        #     if (elem := self.in_root.find(f".//{item.target}")) is not None:
        #         elem.append(item.code)
        #         pass
        #     else:
        #         elem = self.in_root.find(f".//{item.scope}//{item.target}")
        
        ET.indent(self.in_root, space="  ")
        self.in_tree.write(self.output_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
        print(f"Scenario file written to {self.output_path}")

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

    def is_valid(self):
        return self.schema.is_valid(self.output_path)
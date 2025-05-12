from config import *
from openai import OpenAI
from lxml import etree as ET
import xmlschema

class Controller:
    def __init__(self, input_file, disturbance_file, output_file):
        """
        입/출력 자원을 효율적으로 관리하기 위해 클래스로 정의
        기본적인 경로 및 키값에 관한 세팅은 config.py에 정의
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
        
    def gen_disturbance(self, input_text):
        """
        LLM으로부터 자연어 입력을 코드 조각으로 생성

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
                    "content": """
                                당신은 OpenSCENARIO XML 에디터입니다.
                                아래 메타데이터와 code_slice만 답변해줍니다.
                                type: XSD 타입(ex: AddEntityAction, StopTrigger, EnvironmentAction 등)
                                scope: init/global/act/event/scenario
                                code_slice: 실제 XML 조각

                                **룰**
                                1. scope에 따라 적절한 컨테이너(<Init><Actions>, <GlobalAction>, <Act><Actions>, <Event>, <Storyboard>)를 자동으로 찾거나 생성합니다.
                                2. 필요한 상위 노드(예: <Actions> 블록, <Trigger> 또는 <Maneuver> 등)가 없으면, 최소한의 스켈레톤을 덧붙여 code slice가 유효하도록 보완합니다.
                                3. 이미 해당 컨테이너가 존재하면 거기에만 슬라이스를 삽입하고, 중복 노드는 만들지 않습니다.
                                4: 해당하는 전체 코드가 아닌 base secnario에 들어갈 코드 조각만 출력합니다. 
                                """
                },
                {
                    "role": "user",
                    "content": f"""
                                질문: {input_text}
                                base scenario:
                                {ET.tostring(self.in_root).decode()}
                                """
                }
            ]
        )

        content = response.choices[0].message.content
        print(content)
        out_xosc = "<OpenSCENARIO>\n" + "\n".join(content.split('\n')[4:-1]) + "\n</OpenSCENARIO>"

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
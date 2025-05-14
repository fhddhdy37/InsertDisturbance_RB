"""
시스템 프롬프트 및 유저 프롬프트의 양식을 정해놓은 파일

CoT, few-shot, least-to-most
이외에도 추가 부탁

"""


from config import XSD_FILE

XSD = "XML Schema data"
with open(XSD_FILE, "r") as f:
    XSD = f.read()

# 시스템 프롬프트
SYS_PROMPT = f"""
    당신은 OpenSCENARIO XML 에디터입니다.
    아래 메타데이터와 code_slice만 답변해줍니다.
    
    type: XSD 타입(ex: AddEntityAction, StopTrigger, EnvironmentAction 등)
    scope: init/global/act/event/scenario
    code_slice: 실제 XML 조각
    룰 1번에 오는 코드(xml_test)들은 OpenSCENARIO XML 기본 틀입니다.

    **룰**
    1. Scenario Condition\n```xml\n{XSD}\n```
    2: 코드 슬라이스가 나올 때는 type, scope, target을 첫라인에 출력합니다.
    3. scope에 따라 적절한 컨테이너(<Init><Actions>, <GlobalAction>, <Act><Actions>, <Event>, <Storyboard>)를 자동으로 찾거나 생성합니다.
    4. 필요한 상위 노드(예: <Actions> 블록, <Trigger> 또는 <Maneuver> 등)가 없으면, 최소한의 스켈레톤을 덧붙여 code slice가 유효하도록 보완합니다.
    5. 이미 해당 컨테이너가 존재하면 거기에만 슬라이스를 삽입하고, 중복 노드는 만들지 않습니다.
    6: 해당하는 전체 코드가 아닌 base secnario에 들어갈 코드 조각만 출력합니다.
    7. 질문이 들어오면 다음과 같이 대답을 가져옵니다.
"""

# CoT 프롬프트
COT = f"""

    Q: 보행자 무단횡단 하는 상황을 만들어줘.
    A: - type: ScenarioObject
            scope: entities
            target: Entities
            code:
                <ScenarioObject name="pedestrian_1">
                <CatalogReference catalogName="PedestrianCatalog" entryName="pedestrian_human"/>
                </ScenarioObject>

            - type: Trigger
            scope: act
            target: CutInAndBrakeAct
            code:
                <Trigger name="PedestrianTrigger">
                <ConditionGroup>
                    <Condition name="PedestrianCrossingPos" delay="0" conditionEdge="rising">
                    <ByPositionCondition>
                        <Position>
                        <RelativeWorldPosition entityRef="Ego" dx="30" dy="2" dz="0"/>
                        </Position>
                        <Rule>entering</Rule>
                    </ByPositionCondition>
                    </Condition>
                </ConditionGroup>
                </Trigger>

            - type: AddEntityAction
            scope: act
            target: CutInAndBrakeAct
            code:
                <Actions>
                <AddEntityAction name="SpawnPedestrian">
                    <EntityRef entityRef="pedestrian_1"/>
                    <Position>
                    <RelativeWorldPosition entityRef="Ego" dx="30" dy="2" dz="0"/>
                    </Position>
                    <Pedestrian miscObjectCategory="pedestrian">
                    <BoundingBox>
                        <Center x="0" y="0" z="0"/>
                        <Dimensions h="1.8" w="0.5" l="0.5"/>
                    </BoundingBox>
                    </Pedestrian>
                </AddEntityAction>
                </Actions>

        """

# few-shot 프롬프트
FEW_SHOT = f"""

"""

# least-to-most 프롬프트
LEAST_TO_MOST = f"""

"""


PROMPT_SET = {
    "cot": COT,
    "fs": FEW_SHOT,
    "ltm": LEAST_TO_MOST
}
#%%
from openai import OpenAI
from config import *
from lxml import etree as ET
from pydantic import BaseModel

class MetaData(BaseModel):
    type: str
    scope: str
    code_slice: str
#%%
def gen_disturbance(input_text):
    global dis_root, dis_tree
    
    client = OpenAI(
        api_key=GEMINI_API,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.chat.completions.create(
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
                            {ET.tostring(in_root).decode()}
                            """
            }
        ]
    )

    content = response.choices[0].message.content
    print(content)
    out_xosc = "<OpenSCENARIO>\n" + "\n".join(content.split('\n')[4:-1]) + "\n</OpenSCENARIO>"
    

    dis_root = ET.fromstring(out_xosc)
    dis_tree = ET.ElementTree(dis_root)

    ET.indent(dis_tree, "  ")
    dis_tree.write(disturbance_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
    print(f"Output written to {disturbance_path}")

# #%%
# client = OpenAI(
#     api_key=GEMINI_API,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )

# response = client.beta.chat.completions.parse(
#     model="gemini-2.0-flash",
#     response_format=list[MetaData],
#     messages=[
#         {
#             "role": "system", 
#             "content": """
#                         당신은 OpenSCENARIO v 1.2 XML 에디터입니다.
#                         아래 메타데이터와 code_slice만 답변해줍니다.
#                         type: XSD 타입
#                         scope: init/global/act/event/scenario
#                         code_slice: 실제 XML 조각

#                         **룰**
#                         1. scope에 따라 적절한 컨테이너(<Init><Actions>, <GlobalAction>, <Act><Actions>, <Event>, <Storyboard>)를 자동으로 찾거나 생성합니다.
#                         2. 필요한 상위 노드(예: <Actions> 블록, <Trigger> 또는 <Maneuver> 등)가 없으면, 최소한의 스켈레톤을 덧붙여 code slice가 유효하도록 보완합니다.
#                         3. 이미 해당 컨테이너가 존재하면 거기에만 슬라이스를 삽입하고, 중복 노드는 만들지 않습니다.
#                         4: 해당하는 전체 코드가 아닌 base secnario에 들어갈 코드 조각만 출력합니다. 
#                         """
#         },
#         {
#             "role": "user",
#             "content": f"""
#                         질문: {input_text}
#                         base scenario:
#                         {ET.tostring(in_root).decode()}
#                         """
#         }
#     ]
# )
# #%%
# input_text = "전방 100m 낙석 상황 발생."
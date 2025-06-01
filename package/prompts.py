"""
시스템 프롬프트 및 유저 프롬프트의 양식을 정해놓은 파일

CoT, few-shot, least-to-most
이외에도 추가 부탁

"""


from package import XSD_FILE

XSD = "XML Schema data"
with open(XSD_FILE, "r",encoding='utf-8') as f:
    XSD = f.read()

# 시스템 프롬프트
SYS_PROMPT = f"""
You are an OpenSCENARIO XML Editor.  
Users supply only lightweight “slices” in YAML form; you must merge them into a valid base scenario using the rules below.

**Global Rules**  
1. **Slice headers**  
   Each slice must include exactly three fields before the code:  
   - `type`: the XSD element name of the snippet (e.g. `ScenarioObject`, `ManeuverGroup`, `Private`).  
   - `target`: **one of** `Entities`, `Init`, or `Act`, indicating which top-level section of the base scenario it belongs under.  
   - `name`: _optional_; if there are multiple elements with the same `target`, use `name` to pick the right one (e.g. `<Act name="CutInAndBrakeAct">`).  

2. **Code snippet format**  
   The first tag in `code:` must match `target`:  
   - `target: Entities` → code must start with `<ScenarioObject …>`  
   - `target: Init`     → code must start with `<Private …>`  
   - `target: Act`      → code must start with `<ManeuverGroup …>`  

3. **Container insertion**  
   - **If the `target` section exists** in the base scenario, insert your snippet under it (for `Init`, inside its `<Actions>`; for `Act`, inside its `<Actions>`; for `Entities`, directly).  
   - **If it does not exist**, create the minimal skeleton before inserting (e.g. `<Init><Actions>…</Actions></Init>`).

4. **Inline Object Definitions**
To avoid broken or mismatched CatalogReference entries, always 
prefer inlining full object definitions 
(e.g. <MiscObject>, <Vehicle>, <Controller>, etc.) directly within your slice instead of referencing external catalogs.  

5. **Type-to-container fallback**  
   If you omit or mistype `target`, fall back to inserting by `type`:  
   - `ScenarioObject` → under `<Entities>`  
   - `Private` or any `*Action` → under `<Init><Actions>`  
   - `ManeuverGroup` → under the first `<Act><Actions>`  
   (and so on, following the XSD hierarchy)

6. **Output**  
   Return **only** the merged `<OpenSCENARIO>` XML, no extra text.
"""

# CoT 프롬프트
FEW_SHOT = f"""
Q:- 100m 앞 낙석 상황을 발생시켜줘.
A:- type: ScenarioObject
  target: Entities
  code:
    <ScenarioObject name="rockfall_1">
      <MiscObject mass="0" miscObjectCategory="obstacle" name="PE_Firewall_Orange">
        <BoundingBox>
          <Center x="0.5" y="0.0" z="0.5"/>
          <Dimensions width="1.0" length="1.0" height="1.0"/>
        </BoundingBox>
        <Properties>
          <Property name="scale_x" value="1.0"/>
          <Property name="scale_y" value="1.0"/>
          <Property name="scale_z" value="1.0"/>
        </Properties>
      </MiscObject>
    </ScenarioObject>

- type: Private
  target: Init
  code: |
    <Private entityRef="rockfall_1">
      <PrivateAction>
        <TeleportAction>
          <Position>
            <RelativeWorldPosition entityRef="Ego" dx="100" dy="0" dz="0"/>
          </Position>
        </TeleportAction>
      </PrivateAction>
    </Private>

- type: ManeuverGroup
  target: Act
  name: CutInAndBrakeAct
  code: |
    <ManeuverGroup maximumExecutionCount="1" name="RockfallAvoidanceGroup">
      <Actors selectTriggeringEntities="false">
        <EntityRef entityRef="Ego"/>
      </Actors>
      <Maneuver name="RockfallManeuver">
        <Event name="RockfallEvent" priority="overwrite">
          <StartTrigger>
            <ConditionGroup>
              <Condition name="RockfallProximity" delay="0" conditionEdge="rising">
                <ByEntityCondition>
                  <TriggeringEntities triggeringEntitiesRule="all">
                    <EntityRef entityRef="rockfall_1"/>
                  </TriggeringEntities>
                  <EntityCondition>
                    <RelativeDistanceCondition
                      entityRef="rockfall_1"
                      relativeDistanceType="euclidianDistance"
                      freespace="true"
                      routingAlgorithm="assignedRoute"
                      rule="lessThan"
                      value="10"/>
                  </EntityCondition>
                </ByEntityCondition>
              </Condition>
            </ConditionGroup>
          </StartTrigger>
          <Action name="BrakeForRockfall">
            <PrivateAction>
              <LongitudinalAction>
                <SpeedAction>
                  <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="0"/>
                  <SpeedActionTarget>
                    <AbsoluteTargetSpeed value="0"/>
                  </SpeedActionTarget>
                </SpeedAction>
              </LongitudinalAction>
            </PrivateAction>
          </Action>
        </Event>
      </Maneuver>
    </ManeuverGroup>

Q:보행자가 도로를 천천히 침범하는 상황을 만들어줘.
A:- type: ScenarioObject
  target: Entities
  code: |
    <ScenarioObject name="pedestrian_1">
      <Pedestrian mass="75.0" pedestrianCategory="pedestrian" name="AdultPedestrian">
        <BoundingBox>
          <Center x="0.0" y="0.0" z="0.0"/>
          <Dimensions width="0.5" length="0.5" height="1.7"/>
        </BoundingBox>
        <Properties>
          <Property name="walkingSpeed" value="1.5"/>
        </Properties>
      </Pedestrian>
    </ScenarioObject>

- type: Private
  target: Init
  code: |
    <Private entityRef="pedestrian_1">
      <PrivateAction>
        <TeleportAction>
          <Position>
            <RelativeWorldPosition entityRef="Ego" dx="30" dy="2" dz="0"/>
          </Position>
        </TeleportAction>
      </PrivateAction>
    </Private>

- type: ManeuverGroup
  target: Act
  name: CutInAndBrakeAct
  code: |
    <ManeuverGroup maximumExecutionCount="1" name="PedestrianCrossingGroup">
      <Actors selectTriggeringEntities="false">
        <EntityRef entityRef="pedestrian_1"/>
      </Actors>
      <Maneuver name="PedestrianCrossManeuver">
        <Event name="PedestrianCrossEvent" priority="overwrite">
          <StartTrigger>
            <ConditionGroup>
              <Condition name="BeginCrossing" delay="0" conditionEdge="rising">
                <ByValueCondition>
                  <SimulationTimeCondition value="2" rule="greaterThan"/>
                </ByValueCondition>
              </Condition>
            </ConditionGroup>
          </StartTrigger>
          <Action name="WalkAcrossZebra">
            <PrivateAction>
              <LateralAction>
                <LaneOffsetAction continuous="false">
                  <LaneOffsetActionDynamics dynamicsShape="linear" continuous="false" value="3",maxLateralAcc="2.0"/>
                  <LaneOffsetTarget>
                    <RelativeTargetLaneOffset entityRef="pedestrian_1" value="1"/>
                  </LaneOffsetTarget>
                </LaneOffsetAction>
              </LateralAction>
            </PrivateAction>
          </Action>
        </Event>
      </Maneuver>
    </ManeuverGroup>
"""

# few-shot 프롬프트
COT = f"""
    내가 너한테 보낸 질문에 대한 답을 순차적으로 하나씩 생각해가면서 답변을 보내줘.
"""

# least-to-most 프롬프트
LEAST_TO_MOST = f"""
  내가 너한테 보낸 질문에 대한 답을 위하여 나의 질문을 piority가 존재하는 sub problem으로 만들어주고 그 sub problem들을
   하나씩 해결해주며 문제를 해결해줘.
"""


PROMPT_SET = {
    "fs": FEW_SHOT,
    "cot": COT,
    "ltm": LEAST_TO_MOST
}
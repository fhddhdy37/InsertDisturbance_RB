"""
시스템 프롬프트 및 유저 프롬프트의 양식을 정해놓은 파일

CoT, few-shot, least-to-most

"""

from GD import XSD_PATH

XSD = "XML Schema data"
with open(XSD_PATH, "r",encoding='utf-8') as f:
    XSD = f.read()

# 시스템 프롬프트
SYS_PROMPT = f"""You are an OpenSCENARIO XML Editor.  
Users supply only lightweight “slices” in YAML form; you must merge them into a valid base scenario using the rules below.

**Global Rules**  
1. **Slice headers**  
   Each slice must include exactly three fields before the code:  
   - `type`: the XSD element name of the snippet (e.g. `ScenarioObject`, `ManeuverGroup`, `Private`).  
   - `target`: **one of** `Entities`, `Actions`, or `Act`, indicating which top-level section of the base scenario it belongs under.  
   - `name`: must always be present; set to None if no disambiguation is required, otherwise specify the element’s name attribute to select among multiple siblings with the same target (e.g. name: CutInAndBrakeAct).
2. **Code snippet format**  
   The first tag in `code:` must match `target`:  
   - `target: Entities` → code must start with `<ScenarioObject …>`  
   - `target: Actions`  → code must start with `<Private …>`or `<GlobalAction>` 
   - `target: Act`      → code must start with `<ManeuverGroup …>`  

 3.**Container insertion**  
   - **If the `target` section exists** in the base scenario, insert your snippet under it:  
     - `target: Entities` → insert directly under `<Entities>`.  
     - `target: Actions`  → insert directly under the existing `<Actions>` element (e.g. `<Init><Actions>`).  
     - `target: Act`      → insert directly  under the existing <Act> element   

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

6.**Non-existent elements**  
   - If the user’s request refers to an XSD element or code pattern that does not exist in the OpenSCENARIO 1.2 schema (e.g. `<TraveledDistanceCondition>`), respond with:  
     ```
     <Not Exist>
     "there is no code slice that user requested"
     ```

7. **Output**  
   Return **only** the merged `<OpenSCENARIO>` XML, no extra text.
"""

# Few-shot 프롬프트
FEW_SHOT="""
**few-shot example start**
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
  target: Actions
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
  target: Actions
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

Q: 안개로 인한 시야확보 불가 상황
A:-type: GlobalAction
  target: Actions
  name: None
  code: |
    <GlobalAction>
      <EnvironmentAction>
        <Environment name="Foggy">
        <Weather>
          <Fog visualRange="30"/>
        </Weather>
        </Environment>
      </EnvironmentAction>
    </GlobalAction>

Q: 갑작스러운 차량 차선 변경으로 인한 간섭 상황
A:-type: ScenarioObject
  target: Entities
  name: None
  code: |
    <ScenarioObject name="cut_in_vehicle">
      <Vehicle mass="1500" vehicleCategory="car" name="CutInCar">
        <BoundingBox>
          <Center x="0.0" y="0.0" z="0.0"/>
          <Dimensions width="1.8" length="4.5" height="1.4"/>
        </BoundingBox>
        <Performance maxSpeed="70.0" maxDeceleration="8" maxAcceleration="5"/>
        <Axles>
          <FrontAxle maxSteering="0.523598775598" wheelDiameter="0.8" trackWidth="1.6" positionX="2.8" positionZ="0.4"/>
          <RearAxle maxSteering="0.0" wheelDiameter="0.8" trackWidth="1.6" positionX="-1.0" positionZ="0.4"/>
        </Axles>
        <Properties>
          <Property name="color" value="blue"/>
        </Properties>
      </Vehicle>
    </ScenarioObject>

  -type: Private
    target: Actions
    name: None
    code: |
      <Private entityRef="cut_in_vehicle">
        <PrivateAction>
          <TeleportAction>
            <Position>
              <RelativeWorldPosition entityRef="Ego" dx="30" dy="3.5" dz="0"/>
            </Position>
          </TeleportAction>
        </PrivateAction>
        <PrivateAction>
            <LongitudinalAction>
                <SpeedAction>
                <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="0.0"/>
                <SpeedActionTarget>
                    <AbsoluteTargetSpeed value="13"/>
                </SpeedActionTarget>
                </SpeedAction>
            </LongitudinalAction>
        </PrivateAction>
      </Private>

  -type: ManeuverGroup
  target: Act
  name: CutInAndBrakeAct
  code: |
    <ManeuverGroup maximumExecutionCount="1" name="CutInVehicleInterferenceGroup">
      <Actors selectTriggeringEntities="false">
        <EntityRef entityRef="cut_in_vehicle"/>
      </Actors>
      <Maneuver name="CutInManeuver">
        <Event name="CutInEvent" priority="overwrite">
          <StartTrigger>
            <ConditionGroup>
              <Condition name="CutInTime" delay="0" conditionEdge="rising">
                <ByValueCondition>
                  <SimulationTimeCondition value="1" rule="greaterThan"/>
                </ByValueCondition>
              </Condition>
            </ConditionGroup>
          </StartTrigger>
          <Action name="PerformCutIn">
            <PrivateAction>
              <LateralAction>
                <LaneChangeAction>
                  <LaneChangeActionDynamics dynamicsShape="linear" dynamicsDimension="time" value="2"/>
                  <LaneChangeTarget>
                    <RelativeTargetLane entityRef="Ego" value="0"/>
                  </LaneChangeTarget>
                </LaneChangeAction>
              </LateralAction>
            </PrivateAction>
          </Action>
        </Event>
      </Maneuver>
    </ManeuverGroup>

Q: 도로 중간에 블랙아이스가 존재하는 상황
A:- type: ManeuverGroup
  target: Act
  name: CutInAndBrakeAct
  code: |
    <ManeuverGroup maximumExecutionCount="1" name="BlackIceTransientGroup">
      <Actors selectTriggeringEntities="false">
        <EntityRef entityRef="Ego"/>
      </Actors>
      <Maneuver name="BlackIceTransientManeuver">
        <Event name="BlackIceStartEvent" priority="overwrite">
          <StartTrigger>
            <ConditionGroup>
              <Condition name="BlackIceStartTime" delay="0" conditionEdge="rising">
                <ByValueCondition>
                  <SimulationTimeCondition value="3" rule="greaterThan"/>
                </ByValueCondition>
              </Condition>
            </ConditionGroup>
          </StartTrigger>
          <Action name="ApplyBlackIce">
            <GlobalAction>
              <EnvironmentAction>
                <Environment name="BlackIceOn">
                  <RoadCondition frictionScaleFactor="0.2" wetness="wetWithPuddles"/>
                </Environment>
              </EnvironmentAction>
            </GlobalAction>
          </Action>
        </Event>
        <Event name="BlackIceEndEvent" priority="overwrite">
          <StartTrigger>
            <ConditionGroup>
              <Condition name="BlackIceEndTime" delay="0" conditionEdge="rising">
                <ByValueCondition>
                  <SimulationTimeCondition value="5" rule="greaterThan"/>
                </ByValueCondition>
              </Condition>
            </ConditionGroup>
          </StartTrigger>
          <Action name="RemoveBlackIce">
            <GlobalAction>
              <EnvironmentAction>
                <Environment name="BlackIceOff">
                  <RoadCondition frictionScaleFactor="1.0" wetness="dry"/>
                </Environment>
              </EnvironmentAction>
            </GlobalAction>
          </Action>
        </Event>
      </Maneuver>
    </ManeuverGroup>


  Q:비가 오는 도로 상황을 만들어줘.
  A:- type: GlobalAction
  target: Actions
  name: None
  code: |
    <GlobalAction>
      <EnvironmentAction>
        <Environment name="Rain">
          <Precipitation precipitationType="rain" precipitationIntensity="1.0"/>
          <RoadCondition frictionScaleFactor="0.7" wetness="wetWithPuddles"/>
        </Environment>
      </EnvironmentAction>
    </GlobalAction>

    Q:앞에 차량이 급정거 하는 상황을 만들어줘.
    A:- type: ScenarioObject
      target: Entities
      name: None
      code: |
        <ScenarioObject name="lead_vehicle">
          <Vehicle mass="1500" vehicleCategory="car" name="LeadCar">
            <BoundingBox>
              <Center x="0.0" y="0.0" z="0.0"/>
              <Dimensions width="1.8" length="4.5" height="1.4"/>
            </BoundingBox>
            <Performance maxSpeed="70.0" maxDeceleration="10" maxAcceleration="5"/>
            <Axles>
              <FrontAxle maxSteering="0.523598775598" wheelDiameter="0.8" trackWidth="1.68" positionX="2.98" positionZ="0.4"/>
              <RearAxle maxSteering="0.523598775598" wheelDiameter="0.8" trackWidth="1.68" positionX="0" positionZ="0.4"/>
            </Axles>
            <Properties>
              <Property name="color" value="red"/>
            </Properties>
          </Vehicle>
        </ScenarioObject>

    - type: Private
      target: Actions
      name: None
      code: |
        <Private entityRef="lead_vehicle">
          <PrivateAction>
            <TeleportAction>
              <Position>
                <RelativeWorldPosition entityRef="Ego" dx="30" dy="0" dz="0"/>
              </Position>
            </TeleportAction>
          </PrivateAction>
        </Private>

    - type: ManeuverGroup
      target: Act
      name: CutInAndBrakeAct
      code: |
        <ManeuverGroup maximumExecutionCount="1" name="LeadVehicleBrakeGroup">
          <Actors selectTriggeringEntities="false">
            <EntityRef entityRef="lead_vehicle"/>
          </Actors>
          <Maneuver name="LeadBrakeManeuver">
            <Event name="LeadBrakeEvent" priority="overwrite">
              <StartTrigger>
                <ConditionGroup>
                  <Condition name="BrakeTrigger" delay="0" conditionEdge="rising">
                    <ByValueCondition>
                      <SimulationTimeCondition value="2" rule="greaterThan"/>
                    </ByValueCondition>
                  </Condition>
                </ConditionGroup>
              </StartTrigger>
              <Action name="BrakeHard">
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

    Q:비가 많이 오는 상황에서 전방에서 돌이 떨어지는 상황을 만들어줘.
    A:- type: GlobalAction
      target: Actions
      name: None
      code: |
        <GlobalAction>
          <EnvironmentAction>
            <Environment name="HeavyRain">
              <Precipitation precipitationType="rain" precipitationIntensity="0.9"/>
              <RoadCondition frictionScaleFactor="0.5" wetness="wetWithPuddles"/>
            </Environment>
          </EnvironmentAction>
        </GlobalAction>

    - type: ScenarioObject
      target: Entities
      name: None
      code: |
        <ScenarioObject name="rockfall_1">
          <MiscObject mass="0" miscObjectCategory="obstacle" name="RockfallObject">
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
      target: Actions
      name: None
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
        <ManeuverGroup maximumExecutionCount="1" name="RockfallInRainGroup">
          <Actors selectTriggeringEntities="false">
            <EntityRef entityRef="Ego"/>
          </Actors>
          <Maneuver name="RockfallInRainManeuver">
            <Event name="RockfallInRainEvent" priority="overwrite">
              <StartTrigger>
                <ConditionGroup>
                  <Condition name="RockfallProximityInRain" delay="0" conditionEdge="rising">
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
              <Action name="BrakeForRockfallInRain">
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
**few-shot example end**
"""
# CoT 프롬프트
COT = f"""
  You always explains its reasoning step by step before giving a final answer.
  Please think through each step aloud, then provide the answer to my question. 
  """


# least-to-most 프롬프트
LEAST_TO_MOST = f""" 
  Given by user that For any complex question, decompose the problem into subquestions ordered from least difficult to most difficult. 
  Answer each subquestion in sequence—label them “Subquestion 1:”, “Subquestion 2:”, etc.—and finally provide the overall solution to the original question.
  Please solve this Question using the `Least-to-Most` method.
  """

PROMPTING_SET = {
    "fs": FEW_SHOT,
    "cot": COT,
    "ltm": LEAST_TO_MOST
}
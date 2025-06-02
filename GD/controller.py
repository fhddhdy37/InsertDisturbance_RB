from GD import config as cf
from GD.prompts import *

from openai import OpenAI

from lxml import etree as ET
from xmlschema.validators.exceptions import XMLSchemaValidationError
import xmlschema
import traceback

class Controller:
    def __init__(self):
        self.input_path = cf.INPUT_PATH
        self.output_path = cf.OUTPUT_PATH
        self.dist_path = cf.TMP_DIR / f"test_{self.__class__.__name__}_{cf.TIME}.xosc"
        self.schema = xmlschema.XMLSchema(cf.XSD_PATH)

        self.in_tree = ET.parse(self.input_path)
        self.in_root = self.in_tree.getroot()
        self.base_scenario = ET.tostring(self.in_root).decode()
        self.dist_tree = None
        self.dist_root = None
        
        self.client = None
        self.messages = []
        self.response_msg = None
        self.response_data = None
        self.response_count = 0
        self.err = None

    def gen_disturbance(self, input_text, model, *prompting):
        self._set_prompt(input_text, prompting)
        response = self.client.beta.chat.completions.parse(
            model=model,
            response_format=cf.ResponseData,
            temperature=0.5,
            messages=self.messages
        )
        self.response_msg = response.choices[0].message.parsed
        print(self.response_msg)
        self.response_data = response.choices[0].message.parsed.data
        
        response = self.client.chat.completions

        try:
            self._write_disturbance()
        except ET.XMLSyntaxError as e:
            self.err = traceback.format_exc()
            self.gen_disturbance(input_text, model, prompting)

    def _set_prompt(self, input_text, prompting):
        self.response_count += 1
        if self.response_count == 1:
            prompt_engeneering = ""
            for prompt in prompting:
                prompt_engeneering += PROMPTING_SET[prompt.lower()]

            self.messages = [
                {
                    "role": "system",
                    "content": SYS_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
                                {prompt_engeneering}

                                Q: {input_text}
                                base scenario:
                                {self.base_scenario}
                                """
                }
            ]
        elif self.response_count == 2:
            self.messages.append(
                {
                    "role": "assistant",
                    "content": str(self.response_msg)
                }
            )
            self.messages.append(
                {
                    "role": "user",
                    "content": f"""
                                The following error occurred in your code:
                                Error message:
                                {self.err}
                                """
                }
            )
        elif self.response_count > 2:
            self.messages[2] = {
                    "role": "assistant",
                    "content": str(self.response_msg)
            }
            self.messages[3] = {
                    "role": "user",
                    "content": f"""
                                The following error occurred in your code:
                                Error message:
                                {self.err}
                                """                
            }

    def _write_disturbance(self):
        out_xosc = "<OpenSCENARIO>\n"
        for data in self.response_data:
            out_xosc += data.code
            print(f"type: {data.type}, target: {data.target}, name: {data.name}")
        out_xosc += "\n</OpenSCENARIO>"

        self.dist_root = ET.fromstring(out_xosc)
        self.dist_tree = ET.ElementTree(self.dist_root)
        ET.indent(self.dist_tree, "  ")
        self.dist_tree.write(self.dist_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
        print(f"Disturbance file written to {self.dist_path}")

    def insert_scenario(self):
        for item in self.response_data:
            code = ET.fromstring(item.code)
            if item.name == "None":
                parent = self.in_root.find(f".//{item.target}")
            else:
                parent = self.in_root.find(f".//{item.target}[@name='{item.name}']")

            if item.type == "ScenarioObject" or item.type == "Private":
                parent.append(code)
            elif item.type == "GlobalAction" or item.type == "ManeuverGroup":
                parent.insert(0, code)

        ET.indent(self.in_root, space="  ")
        self.in_tree.write(self.output_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
        print(f"Scenario file written to {self.output_path}")

    def is_valid(self):
        return self.schema.is_valid(self.output_path)

    def validate(self):
        try:
            self.schema.validate(self.output_path)
        except XMLSchemaValidationError as e:
            print(e)
            return False
        else:
            print("valid")
            return True

class GPTController(Controller):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            api_key=cf.GPT_API
        )
        

class GeminiController(Controller):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            api_key=cf.GEMINI_API,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

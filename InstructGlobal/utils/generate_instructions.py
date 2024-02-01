import json
from json import JSONDecodeError
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import pandas as pd

# import os, openlayer
# from openlayer import llm_monitors
# OPENLAYER_API_KEY = "IOQJI7Ez4IbsouOIPZPithJRxSaVR3Yy"
# OPENLAYER_PROJECT_NAME = "My project"
# os.environ["OPENLAYER_API_KEY"] = OPENLAYER_API_KEY
# os.environ["OPENLAYER_PROJECT_NAME"] = OPENLAYER_PROJECT_NAME

class Generate:
    def __init__(self, openai_api_key, model, n):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.n = n
        # monitor = llm_monitors.OpenAIMonitor(client=self.client, publish=True)
        # monitor.start_monitoring()

    def create_instructions(self, prompt, batch_size):
        # Run the generator and get the DataFrame
        df = self.run(prompt, batch_size)

        # Convert the DataFrame to a list of dictionaries
        instructions = df.to_dict('records')

        return instructions

    def run(self, prompt, n):
        self.prompt = prompt
        self.n = n

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "q_and_a",
                    "description": "questions and answers broken up into instructions, inputs, and outputs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            **{f"Instruction {i+1}": {
                                "type": "string",
                                "description": "instruction",
                            } for i in range(self.n)},
                            **{f"Input {i+1}": {
                                "type": "string",
                                "description": "input",
                            } for i in range(self.n)},
                            **{f"Output {i+1}": {
                                "type": "string",
                                "description": "output",
                            } for i in range(self.n)}
                        },
                        "required": [f"Instruction {i+1}" for i in range(self.n)] + [f"Input {i+1}" for i in range(self.n)] + [f"Output {i+1}" for i in range(self.n)],
                    },
                }
            },
        ]

        response = self.generate_instructions("q_and_a")
        # extract output into df
        function_call = response.choices[0].message.tool_calls[0].function
        try:
            arguments = json.loads(function_call.arguments)
        except JSONDecodeError:
            arguments = {}
        arguments = json.loads(function_call.arguments)
        instructions = {k: v for k, v in arguments.items() if "Instruction" in k}
        inputs = {k: v for k, v in arguments.items() if "Input" in k}
        outputs = {k: v for k, v in arguments.items() if "Output" in k}
        df = pd.DataFrame({
            'instruction_en': [instructions.get(f"Instruction {i}") for i in range(1, self.n+1)],
            'input_en': [inputs.get(f"Input {i}") for i in range(1, self.n+1)],
            'output_en': [outputs.get(f"Output {i}") for i in range(1, self.n+1)]
        })
        
        # Extract completion_tokens and prompt_tokens
        # completion_tokens = response.usage.completion_tokens
        # prompt_tokens = response.usage.prompt_tokens

        return df

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def generate_instructions(self, tool_name):
        messages = [{"role": "user", "content": self.prompt}]
        # print(f"API Call Parameters: Model: {self.model}, Messages: {messages}, Tools: {self.tools}") - this works
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice={"type": "function", "function": {"name": tool_name}}
            )
            # print(f"Response: {response}") - this doesn't work
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e
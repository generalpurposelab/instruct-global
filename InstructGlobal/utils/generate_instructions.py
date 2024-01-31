import json
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import pandas as pd

class Generate:
    def __init__(self, openai_api_key, model, prompt, n):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.prompt = prompt
        self.n = n

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
        arguments = json.loads(function_call.arguments)
        instructions = {k: v for k, v in arguments.items() if "Instruction" in k}
        inputs = {k: v for k, v in arguments.items() if "Input" in k}
        outputs = {k: v for k, v in arguments.items() if "Output" in k}
        df = pd.DataFrame({
            'Instruction': [instructions.get(f"Instruction {i}") for i in range(1, self.n+1)],
            'Input': [inputs.get(f"Input {i}") for i in range(1, self.n+1)],
            'Output': [outputs.get(f"Output {i}") for i in range(1, self.n+1)]
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
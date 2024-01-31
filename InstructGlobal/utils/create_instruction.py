import pandas as pd

from InstructGlobal.utils.construct_prompt import ConstructPrompt
from InstructGlobal.utils.generate_instructions import Generate

class CreateInstruction:
    OUTPUT_FILE_FORMAT = "{output_dir}/instruct-global-{language_code}.csv"

    def __init__(self, input_dir, openai_api_key, model):
        self.construct = ConstructPrompt()
        self.generate = Generate(openai_api_key, model, "", 0)  
        self.input_dir = input_dir

    def process_task(self, n, task_category, csv_file, output_schema, output_dir, language_code, target_language):
        # print(input_schema_row)
        input_schema_row = csv_file
        prompt = self.construct.run(n, task_category, input_schema_row, output_schema, target_language)
        self.generate.prompt = prompt
        self.generate.n = n
        qa = self.generate.run(prompt, n)  
        # add translation
        # add insert data
        self.append_to_output(qa, output_dir, language_code)

    def append_to_output(self, final_qa, output_dir, language_code):
        output_file_path = self.OUTPUT_FILE_FORMAT.format(output_dir=output_dir, language_code=language_code)
        if not pd.io.common.file_exists(output_file_path):
            final_qa.to_csv(output_file_path, index=False)
        else:
            final_qa.to_csv(output_file_path, mode='a', header=False, index=False)
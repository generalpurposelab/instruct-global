import json

from InstructGlobal.utils.run_checks import Check
from InstructGlobal.utils.create_output_csv import CreateCSV
from InstructGlobal.utils.load_schema import LoadSchema, FileHandler
from InstructGlobal.utils.generate_instructions import Generate
from InstructGlobal.utils.translate_instructions import Translator
from InstructGlobal.utils.process_csv import CSVProcessor
from InstructGlobal.utils.construct_prompt import PromptConstructor

BATCH_SIZE = 5

class InstructGlobal:
    def __init__(self, openai_api_key, target_language, language_code, model="gpt-3.5-turbo", input_dir="input", output_dir="output", size=50000, google_project_id=None, translation_model="google"):
        self.openai_api_key = openai_api_key
        self.model = model
        self.target_language = target_language
        self.language_code = language_code
        self.size = size
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.check = Check(input_dir, openai_api_key, model, target_language, language_code, size)
        self.load_schema = LoadSchema(size)
        self.output_schema = self.load_schema.load_output_schema()
        self.input_schema = self.load_schema.load_input_schema()
        self.csv_processor = CSVProcessor(self.output_dir, self.language_code, BATCH_SIZE, self.input_schema, self.input_dir)
        self.prompt_constructor = PromptConstructor(self.output_schema, self.input_schema, self.language_code)
        self.generator = Generate(self.openai_api_key, self.model, BATCH_SIZE)
        flores_data = FileHandler.read_csv('InstructGlobal/data/flores.csv')
        self.flores = {row['language_code']: row['flores_code'] for row in flores_data}
        self.translator = Translator(project_id=google_project_id, translation_model=translation_model, flores=self.flores)
        with open('InstructGlobal/data/prompts.json', 'r') as f:
            self.prompts = json.load(f)

    def translate(self, instructions):
        return self.translator.translate_instructions(instructions, self.language_code)

    def create_and_run_csv(self):
        csv_creator = CreateCSV(self.output_dir, self.language_code, self.output_schema, self.input_schema, self.input_dir)
        csv_creator.construct_csv()

    def run(self):
        # Run checks
        self.check.run()
        if not self.check.confirm():
            return
        self.create_and_run_csv()
        self.csv_processor.process_csv(self.translate, self.generator.create_instructions, self.prompt_constructor.construct_prompt)
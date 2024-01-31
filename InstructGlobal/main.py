import csv
import json

from InstructGlobal.utils.check_schema import Check
from InstructGlobal.utils.create_csv import CreateCSV
from InstructGlobal.utils.load_schema import LoadSchema, FileHandler
from InstructGlobal.utils.generate_instructions import Generate
from InstructGlobal.utils.translate_instructions import Translator

BATCH_SIZE = 10

class InstructGlobal:
    def __init__(self, api_key, target_language, language_code, model="gpt-3.5-turbo", input_dir="input", output_dir="output", size=50000, google_project_id="global-instruct"):
        self.api_key = api_key
        self.model = model
        self.target_language = target_language
        self.language_code = language_code
        self.size = size
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.check = Check(input_dir, api_key, model, target_language, language_code, size)
        self.load_schema = LoadSchema(size)
        self.output_schema = self.load_schema.load_output_schema()
        self.input_schema = self.load_schema.load_input_schema()
        self.translator = Translator(project_id=google_project_id)
        with open('InstructGlobal/data/prompts.json', 'r') as f:
            self.prompts = json.load(f)

    def process_csv(self):
        csv_file_path = f"{self.output_dir}/instruct-global-{self.language_code}.csv"
        csv_data = FileHandler.read_csv(csv_file_path)

        # Initialize batch and its source and category
        batch = []
        batch_source = csv_data[0]['source']
        batch_category = csv_data[0]['category']

        # Open the CSV file in write mode to write the header
        with open(csv_file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()

        # Process rows in batches
        for row in csv_data:
            if row['source'] == batch_source and row['category'] == batch_category and len(batch) < BATCH_SIZE:
                batch.append(row)
            else:
                # Process the batch and write it to the CSV file
                self.process_and_write_batch(batch, csv_file_path)

                # Start a new batch
                batch = [row]
                batch_source = row['source']
                batch_category = row['category']

        # Process the last batch and write it to the CSV file
        self.process_and_write_batch(batch, csv_file_path)

    def process_and_write_batch(self, batch, csv_file_path):
        # Construct a single prompt for the entire batch
        batch_row = batch[0]
        batch_size=len(batch)
        prompt_data = self.construct_prompt(category=batch_row['category'], prompt='prompt_no_variables' if batch_row['source'] == 'self-instruct' else 'prompt_variables', csv=batch_row['source'], batch_size=batch_size)

        # Feed the prompt into create_instructions function
        instructions = self.create_instructions(prompt_data, batch_size)
        
        # translate the instructions
        translated_instructions = self.translate(instructions)

        # Update each row in the batch with the corresponding instruction
        for i, row in enumerate(batch):
            row.update(instructions[i])
            row.update(translated_instructions[i])

        # Write the batch to the CSV file
        with open(csv_file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=batch[0].keys())
            writer.writerows(batch)
    
    def translate(self, instructions):
        # Initialize a list to store the translated instructions
        translated_instructions = []

        # Iterate over the instructions
        for instruction in instructions:
            # Translate the instruction, input, and output
            translated_instruction = self.translator.translate_text(instruction['instruction_en'], self.language_code)
            translated_input = self.translator.translate_text(instruction['input_en'], self.language_code)
            translated_output = self.translator.translate_text(instruction['output_en'], self.language_code)

            # Check if the translation was successful
            if not isinstance(translated_instruction, str):
                translated_instruction = translated_instruction.translations[0].translated_text
            if not isinstance(translated_input, str):
                translated_input = translated_input.translations[0].translated_text
            if not isinstance(translated_output, str):
                translated_output = translated_output.translations[0].translated_text

            # Add the translated instruction, input, and output to the list
            translated_instructions.append({
                f'instruction_{self.language_code}': translated_instruction,
                f'input_{self.language_code}': translated_input,
                f'output_{self.language_code}': translated_output,
            })

        return translated_instructions

    def create_instructions(self, prompt, batch_size):
        # Initialize the Generate class
        generator = Generate(self.api_key, self.model, prompt, batch_size)

        # Run the generator and get the DataFrame
        df = generator.run(prompt, batch_size)

        # Convert the DataFrame to a list of dictionaries
        instructions = df.to_dict('records')
        # print(instructions)

        return instructions

    def construct_prompt(self, category, prompt, csv, batch_size):
        # Fetch the corresponding prompt from prompts.json
        prompt_template = self.prompts[prompt]
        
        if prompt == 'prompt_no_variables':
            new_prompt = prompt_template.format(
                n=batch_size,
                task_category=category,
                task_description=self.output_schema[category]['task_description'],
                target_language=self.target_language,
                av_length=self.output_schema[category]['av_length'],
                length_std=self.output_schema[category]['length_std'],
            )
        else:
            input_schema_row = next((row for row in self.input_schema[category] if row['file_name'] == csv), None)
            new_prompt = prompt_template.format(
                n=batch_size,
                task_category=category,
                task_description=self.output_schema[category]['task_description'],
                dataset_description=input_schema_row['description'],
                num_variables=input_schema_row['num_variables'],
                variable_placeholders=', '.join([f'{{variable_{i}}}' for i in range(1, int(input_schema_row['num_variables']) + 1)]),
                variable_descriptions=', '.join([input_schema_row[f'variable_{i}_description'] for i in range(1, int(input_schema_row['num_variables']) + 1)]),                
            )
        return new_prompt

    
    def create_and_run_csv(self):
        csv_creator = CreateCSV(self.output_dir, self.language_code, self.output_schema, self.input_schema, self.input_dir)
        csv_creator.construct_csv()

    def run(self):
        # Run checks
        self.check.run()
        # Use confirm from Check
        if not self.check.confirm():
            return
        self.create_and_run_csv()
        self.process_csv()
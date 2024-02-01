# process_csv

import csv
from InstructGlobal.utils.load_schema import FileHandler
from InstructGlobal.utils.evaluate_output import Evaluate

class CSVProcessor:
    def __init__(self, output_dir, language_code, batch_size, input_schema, input_dir):
        self.output_dir = output_dir
        self.language_code = language_code
        self.batch_size = batch_size
        self.input_schema = input_schema
        self.input_dir = input_dir
        self.total_failures = 0

    def process_csv(self, translator, create_instructions, construct_prompt):
        csv_file_path = f"{self.output_dir}/instruct-global-{self.language_code}.csv"
        csv_data = FileHandler.read_csv(csv_file_path)

        # Load source data once before processing batches
        source_data = None
        source_data_index = 0

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
            if row['source'] == batch_source and row['category'] == batch_category and len(batch) < self.batch_size:
                batch.append(row)
            else:
                # Process the batch and write it to the CSV file
                source_data_index = self.process_and_write_batch(batch, csv_file_path, translator, create_instructions, construct_prompt, source_data_index, source_data)

                # Start a new batch
                batch = [row]
                batch_source = row['source']
                batch_category = row['category']

        # Process the last batch and write it to the CSV file
        self.process_and_write_batch(batch, csv_file_path, translator, create_instructions, construct_prompt, source_data_index, source_data)

        # Write the total number of failures to a .txt file
        failures_file_path = f"{self.output_dir}/failures-{self.language_code}.txt"
        with open(failures_file_path, 'w') as f:
            f.write(f"Total failures: {self.total_failures}\n")

    def get_num_variables(self, category, source):
        for cat in self.input_schema[category]:
            if cat['file_name'] == source:
                return cat['num_variables']
        return None
    
    def validate_instructions(self, instructions, num_variables, corresponding_source_rows):
        num_variables = int(num_variables) if isinstance(num_variables, str) else num_variables
        for instruction in instructions:
            combined_instruction = instruction['instruction_en'] + instruction.get('input_en', '') + instruction.get('output_en', '')
            for n in range(1, num_variables + 1):
                variable_placeholder = f"{{variable_{n}}}"
                if variable_placeholder not in combined_instruction:
                    return False
        return True
    
    def process_and_write_batch(self, batch, csv_file_path, translator, create_instructions, construct_prompt, source_data_index=0, source_data=None):
        batch_row = batch[0]
        batch_size = len(batch)
        prompt_data = construct_prompt(category=batch_row['category'], prompt='prompt_no_variables' if batch_row['source'] == 'self-instruct' else 'prompt_variables', csv=batch_row['source'], batch_size=batch_size)

        if batch_row['source'] != 'self-instruct':
            if source_data is None:
                source_csv_path = f"{self.input_dir}/{batch_row['source']}"
                with open(source_csv_path, mode='r', newline='') as source_file:
                    source_csv_reader = csv.DictReader(source_file)
                    source_data = [row for row in source_csv_reader]

            corresponding_source_rows = source_data[source_data_index:source_data_index + batch_size]

            max_attempts = 10
            attempt = 0
            while attempt < max_attempts:
                instructions = create_instructions(prompt_data, batch_size)
                num_variables = self.get_num_variables(batch_row['category'], batch_row['source'])
                num_variables = int(num_variables) if num_variables and isinstance(num_variables, str) else num_variables

                if self.validate_instructions(instructions, num_variables, corresponding_source_rows):
                    # Replace variable placeholders before translation
                    for i, instruction in enumerate(instructions):
                        for n in range(1, num_variables + 1):
                            variable_placeholder = f"{{variable_{n}}}"
                            variable_value = corresponding_source_rows[i][f'variable_{n}']
                            for field in ['instruction_en', 'input_en', 'output_en']:
                                if field in instruction:
                                    instruction[field] = instruction[field].replace(variable_placeholder, variable_value)

                    translated_instructions = translator(instructions)
                    for i, row in enumerate(batch):
                        row.update(instructions[i])
                        row.update(translated_instructions[i])

                    with open(csv_file_path, 'a', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=batch[0].keys())
                        writer.writerows(batch)
                    break
                else:
                    self.total_failures += 1
                    attempt += 1
                    print(f"Failed attempt #{attempt} - trying again.")

            if attempt == max_attempts:
                print("Failed to validate instructions after maximum attempts.")

            return source_data_index + batch_size
        else:
            instructions = create_instructions(prompt_data, batch_size)
            # For 'self-instruct' source, you might still need to replace placeholders if applicable
            translated_instructions = translator(instructions)
            for i, row in enumerate(batch):
                row.update(instructions[i])
                row.update(translated_instructions[i])

            with open(csv_file_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=batch[0].keys())
                writer.writerows(batch)

            return source_data_index
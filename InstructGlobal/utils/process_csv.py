import csv
from InstructGlobal.utils.load_schema import FileHandler
from InstructGlobal.utils.evaluate_output import Evaluate

class CSVProcessor:
    def __init__(self, output_dir, language_code, batch_size, input_schema):
        self.output_dir = output_dir
        self.language_code = language_code
        self.batch_size = batch_size
        self.input_schema = input_schema

    def process_csv(self, translator, create_instructions, construct_prompt):
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
            if row['source'] == batch_source and row['category'] == batch_category and len(batch) < self.batch_size:
                batch.append(row)
            else:
                # Process the batch and write it to the CSV file
                self.process_and_write_batch(batch, csv_file_path, translator, create_instructions, construct_prompt)

                # Start a new batch
                batch = [row]
                batch_source = row['source']
                batch_category = row['category']

        # Process the last batch and write it to the CSV file
        self.process_and_write_batch(batch, csv_file_path, translator, create_instructions, construct_prompt)

    def get_num_variables(self, category, source):
        for cat in self.input_schema[category]:
            if cat['file_name'] == source:
                return cat['num_variables']
        return None
    
    def validate_instructions(self, instructions, num_variables):
        num_variables = int(num_variables) if isinstance(num_variables, str) else num_variables
        for instruction in instructions:
            combined_instruction = instruction['instruction_en'] + instruction.get('input_en', '') + instruction.get('output_en', '')
            for n in range(1, num_variables + 1):
                variable_placeholder = f"{{variable_{n}}}"
                if variable_placeholder not in combined_instruction:
                    return False
        return True
    
    def process_and_write_batch(self, batch, csv_file_path, translator, create_instructions, construct_prompt):
        # Construct a single prompt for the entire batch
        
        batch_row = batch[0]
        batch_size = len(batch)
        prompt_data = construct_prompt(category=batch_row['category'], prompt='prompt_no_variables' if batch_row['source'] == 'self-instruct' else 'prompt_variables', csv=batch_row['source'], batch_size=batch_size)

        print(batch_row['source'])
        if batch_row['source'] != 'self-instruct':  # Equivalent to checking if prompt == 'prompt_variables'
            max_attempts = 5  # Maximum number of attempts to validate instructions
            attempt = 0  # Current attempt number

            while attempt < max_attempts:
                # Feed the prompt into create_instructions function
                instructions = create_instructions(prompt_data, batch_size)
                # print(instructions)

                num_variables = self.get_num_variables(batch_row['category'], batch_row['source'])

                if self.validate_instructions(instructions, num_variables):
                    # If validation passes, proceed with translation and writing to CSV
                    translated_instructions = translator(instructions)

                    # Update each row in the batch with the corresponding instruction
                    for i, row in enumerate(batch):
                        row.update(instructions[i])
                        row.update(translated_instructions[i])

                    # Write the batch to the CSV file
                    with open(csv_file_path, 'a', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=batch[0].keys())
                        writer.writerows(batch)
                    break  # Exit the loop since validation passed
                else:
                    # If validation fails, increment attempt and possibly modify prompt_data or handle differently
                    print(f"Attempt {attempt + 1} failed. Retrying...")
                    attempt += 1

            if attempt == max_attempts:
                # Handle the case where validation never passes
                print("Failed to validate instructions after maximum attempts.")
        else:
            # Handle the 'prompt_no_variables' case
            # Since there are no variables to validate, you might directly proceed with translation and writing to CSV
            # Feed the prompt into create_instructions function
            instructions = create_instructions(prompt_data, batch_size)
            print(instructions)

            # Translate the instructions
            translated_instructions = translator(instructions)

            # Update each row in the batch with the corresponding instruction
            for i, row in enumerate(batch):
                row.update(instructions[i])
                row.update(translated_instructions[i])

            # Write the batch to the CSV file
            with open(csv_file_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=batch[0].keys())
                writer.writerows(batch)
import csv
from InstructGlobal.utils.load_schema import FileHandler
from InstructGlobal.utils.evaluate_output import Evaluate

class CSVProcessor:
    def __init__(self, output_dir, language_code, batch_size):
        self.output_dir = output_dir
        self.language_code = language_code
        self.batch_size = batch_size

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

    def process_and_write_batch(self, batch, csv_file_path, translator, create_instructions, construct_prompt):
        # Construct a single prompt for the entire batch
        batch_row = batch[0]
        batch_size=len(batch)
        prompt_data = construct_prompt(category=batch_row['category'], prompt='prompt_no_variables' if batch_row['source'] == 'self-instruct' else 'prompt_variables', csv=batch_row['source'], batch_size=batch_size)

        # Feed the prompt into create_instructions function
        instructions = create_instructions(prompt_data, batch_size)

        evaluator = Evaluate(instructions, batch, csv_file_path)
        instructions = evaluator.run()
            
        # translate the instructions
        translated_instructions = translator(instructions)

        # Update each row in the batch with the corresponding instruction
        for i, row in enumerate(batch):
            row.update(instructions[i])
            row.update(translated_instructions[i])

        # Write the batch to the CSV file
        with open(csv_file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=batch[0].keys())
            writer.writerows(batch)
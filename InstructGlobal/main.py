import os
import csv
import json
import math
import random
from tqdm import tqdm

from InstructGlobal.utils.check_schema import Check
from InstructGlobal.utils.create_instruction import CreateInstruction

class FileHandler:
    @staticmethod
    def read_csv(file_path):
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)

    @staticmethod
    def load_json(file_path):
        with open(file_path) as json_file:
            return json.load(json_file)

class InstructGlobal:
    MAX_TASKS_PER_ITERATION = 5
    def __init__(self, api_key, target_language, language_code, model="gpt-3.5-turbo", input_dir="input", output_dir="output", size=50000):
        self.target_language = target_language
        self.language_code = language_code
        self.size = size
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.max_tasks_per_iteration = InstructGlobal.MAX_TASKS_PER_ITERATION
        self.create_instruction = CreateInstruction(input_dir, api_key, model)  
        self.check = Check(input_dir, api_key, model, target_language, language_code)
        self.output_schema = self.load_output_schema()
        self.input_schema = self.load_input_schema()

    def load_output_schema(self):
        """
        Creates dict from output_schema.csv
        """
        output_schema_data = FileHandler.read_csv("InstructGlobal/data/output_schema.csv")
        output_schema = {row['task_category'].strip().lower(): {
            'task_description': row['task_description'].strip(),
            'total_n': math.ceil((self.size * float(row['percent'].strip()))),
            'av_length': row['av_length'].strip(),
            'length_std': row['length_std'].strip()
        } for row in output_schema_data}
        return output_schema

    def load_input_schema(self):
        """
        Creates dict from input_schema.csv
        """
        input_schema_data = FileHandler.read_csv("input/input_schema.csv")
        input_schema = {}
        for row in input_schema_data:
            category = row['category'].strip()
            input_schema.setdefault(category, []).append(row)
        return input_schema

    def load_seeds(self, task_category):
        data = FileHandler.load_json('InstructGlobal/data/seed_tasks.jsonl')
        data = [item for item in data if item['category'] == task_category]
        return random.sample(data, 1)

    def run_checks(self):
        self.check.run()

    def confirm(self):
        print(f"InstructGlobal is initialized to create a {self.size} row dataset in {self.target_language} (language code: {self.language_code})")
        proceed = input("Do you want to proceed? (yes/no): ")
        if proceed.lower() not in ["yes", "y"]:
            print("InstructGlobal cancelled")
            return False
        return True

    def process_task(self, total_n, task_category, csv_file=None, pbar=None):
        """
        Process a task for a given category and CSV file.

        Parameters:
        total_n (int): The total number of tasks to process.
        task_category (str): The category of the task.
        csv_file (str): The path to the CSV file containing the task data. If None, an empty task is processed.

        Returns:
        None
        """
        i = 0
        if csv_file:
            csv_file_name = csv_file['file_name']
            csv_file_path = os.path.join(self.input_dir, f'{csv_file_name}')
            input_data = FileHandler.read_csv(csv_file_path)
            header = input_data[0]
            # i = 1
            while i < total_n:
                n = min(self.MAX_TASKS_PER_ITERATION, total_n - i)
                if i < len(input_data):
                    row = input_data[i]
                    input_data_row = dict(zip(header, row))
                    # print(input_data_row)
                    input_data_row.setdefault('num_variables', '0')
                    self.create_instruction.process_task(n, task_category, input_data_row, self.output_schema[task_category.strip().lower()], self.output_dir, self.language_code, self.target_language)
                i += 1
                if pbar is not None:
                    pbar.update(n)
        else:  # If csv_files is empty
            input_data_row = {'num_variables': '0'}
            while i < total_n:
                n = min(self.MAX_TASKS_PER_ITERATION, total_n - i)
                self.create_instruction.process_task(n, task_category, input_data_row, self.output_schema[task_category.strip().lower()], self.output_dir, self.language_code, self.target_language)
                i += 1
                if pbar is not None:
                    pbar.update(n)

    def create_instructions(self):
        """
        Create instructions for all task categories.

        Returns:
        None
        """
        total_tasks = sum(info['total_n'] for info in self.output_schema.values())
        with tqdm(total=total_tasks, desc="Processing tasks", ncols=70) as pbar:
            for task_category, task_info in self.output_schema.items():
                total_n = task_info['total_n']
                csv_files = self.input_schema.get(task_category, [])  # Get all csv files for this task_category, default to empty list if not found
                if csv_files:  # If csv_files is not empty
                    for csv_file in csv_files:
                        self.process_task(total_n, task_category, csv_file, pbar)
                else:  # If csv_files is empty
                    self.process_task(total_n, task_category, pbar=pbar)
    
    def run(self):
        """
        Runs instruct-global.

        Returns:
        None
        """
        self.run_checks()
        if not self.confirm():
            return
        self.create_instructions()
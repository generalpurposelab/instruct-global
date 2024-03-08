import csv
import json

class FileHandler:
    """
    A utility class for handling file operations.
    """            
    @staticmethod
    def read_csv(file_path):
        """
        Reads a CSV file and returns a list of dictionaries, each representing a row. Used for loading input and output schemas.
        """
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)

    @staticmethod
    def load_json(file_path):
        """
        Loads a JSON file and returns its content.
        """
        with open(file_path) as json_file:
            return json.load(json_file)

class LoadSchema:
    """
    Handles the loading of input and output schemas from files.
    """
    def __init__(self, size):
        self.size = size

    def load_output_schema(self):
        """
        Loads the output schema from a CSV file, processes it, and returns a dictionary.
        """
        output_schema_data = FileHandler.read_csv("InstructGlobal/data/output_schema.csv")
        output_schema = {}
        for row in output_schema_data:
            category = row['task_category'].strip().lower()
            percent = float(row['percent'].strip())
            number_instructions = round(percent * self.size)
            output_schema[category] = {
                'task_description': row['task_description'].strip(),
                'percent': percent,
                'number_instructions': number_instructions,
                'av_length': row['av_length'].strip(),
                'length_std': row['length_std'].strip()
            }
        return output_schema

    def load_input_schema(self):
        """
        Loads the input schema from a CSV file and organizes it into a dictionary.
        """
        input_schema_data = FileHandler.read_csv("input/input_schema.csv")
        input_schema = {}
        for row in input_schema_data:
            category = row['category'].strip()
            input_schema.setdefault(category, []).append(row)
        return input_schema
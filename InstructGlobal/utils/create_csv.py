import csv

class CreateCSV:
    """
    CreateCSV is a class designed to construct an output CSV file from given input and output schemas.
    It reads data from input files, processes them according to the output schema, and writes it to a CSV file.

    Attributes:
        SELF_INSTRUCT (str): A constant used to indicate where answers will be generated using self-instruction.
        output_dir (str): The directory where the output CSV file will be saved.
        language_code (str): The language code used to construct the CSV file.
        output_schema (dict): The schema used to construct the output CSV file.
        input_schema (dict): The schema of the input files.
        input_dir (str): The directory where the input files are located.
        file_rows (dict): A dictionary to store the rows of each input file.
        file_counts (dict): A dictionary to store the count of processed rows for each input file.
    """

    SELF_INSTRUCT = 'self-instruct'

    def __init__(self, output_dir, language_code, output_schema, input_schema, input_dir):
        """
        Initializes the CreateCSV object with the given parameters.

        Args:
            output_dir (str): The directory where the output CSV file will be saved.
            language_code (str): The language code that will be used to construct the dataset.
            output_schema (dict): The schema used to construct the output CSV file.
            input_schema (dict): The schema of the input files.
            input_dir (str): The directory where the input files are located.
        """
        self.output_dir = output_dir
        self.language_code = language_code
        self.output_schema = output_schema
        self.input_schema = input_schema
        self.input_dir = input_dir
        self.file_rows = {}
        self.file_counts = {}

    def write_empty_row(self, writer, category, source):
        writer.writerow({
            'instruction_en': '',  
            f"instruction_{self.language_code}": '',  
            'input_en': '',  
            f"input_{self.language_code}": '',  
            'output_en': '',  
            f"output_{self.language_code}": '',  
            'category': category,
            'source': source
        })

    def load_file_rows(self, file_name):
        with open(f"{self.input_dir}/{file_name}", 'r') as input_f:
            reader = csv.DictReader(input_f)
            self.file_rows[file_name] = list(reader)
            self.file_counts[file_name] = 0

    def handle_input_files(self, input_files, category, writer, details):
        while input_files:
            file_name = input_files[0]
            if file_name not in self.file_rows:
                self.load_file_rows(file_name)
            if self.file_rows[file_name] and self.file_counts[file_name] < details['number_instructions']:
                row = self.file_rows[file_name].pop(0)
                self.write_empty_row(writer, category, file_name)
                self.file_counts[file_name] += 1
            else:
                input_files.pop(0)

    def construct_csv(self):
        with open(f"{self.output_dir}/instruct-global-{self.language_code}.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "instruction_en", 
                f"instruction_{self.language_code}", 
                "input_en", 
                f"input_{self.language_code}", 
                "output_en", 
                f"output_{self.language_code}", 
                "category", 
                "source"
            ])
            writer.writeheader()
            for category, details in self.output_schema.items():
                input_files = [row['file_name'] for row in self.input_schema.get(category, [])]
                for _ in range(details['number_instructions']):
                    if input_files:
                        self.handle_input_files(input_files, category, writer, details)
                    else:
                        self.write_empty_row(writer, category, self.SELF_INSTRUCT)
        print(f"instruct-global-{self.language_code}.csv file initialized in /{self.output_dir}")
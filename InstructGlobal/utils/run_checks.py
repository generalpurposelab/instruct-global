import os
import pandas as pd

class Check:
    """
    Runs initial checks before processing data.
    """
    def __init__(self, input_dir, api_key, model, target_language, language_code, size):
        self.input_dir = input_dir
        self.api_key = api_key
        self.model = model
        self.target_language = target_language
        self.language_code = language_code
        self.size = size

        if not self.api_key:
            print("Error: API key is not provided.")
        if not self.model:
            print("Error: Model not provided.")
        if not self.target_language:
            print("Error: Target language is not provided.")
        if not self.language_code:
            print("Error: Language code is not provided.")

    def run(self):
        # 1) Check whether input_schema.csv is present in input_dir
        schema_file = os.path.join(self.input_dir, 'input_schema.csv')
        if not os.path.exists(schema_file):
            print("Error: input_schema.csv is not present in input_dir.")
            return

        # Load the schema file
        schema_df = pd.read_csv(schema_file)

        # 2) Check whether the columns match
        expected_columns = ['file_name', 'category', 'description']
        if not all(column in schema_df.columns for column in expected_columns):
            print("Error: The columns in input_schema.csv do not match the expected columns: 'file_name', 'category', and 'description'.")
            return

        # 3) Check whether files listed in file_name are present in input_dir
        for file_name in schema_df['file_name']:
            if not os.path.exists(os.path.join(self.input_dir, file_name)):
                print(f"Error: The file {file_name} listed in input_schema.csv is not present in input_dir.")
                return

        # 4) Check whether values are present in category and description for each row
        for index, row in schema_df.iterrows():
            if pd.isnull(row['category']) or pd.isnull(row['description']):
                print(f"Error: Missing values in category or description for the file {row['file_name']}.")
                return
    
    def confirm(self):
        print(f"InstructGlobal is initialized to create a {self.size} row dataset in {self.target_language} (language code: {self.language_code})")
        proceed = input("Do you want to proceed? (yes/no): ")
        if proceed.lower() not in ["yes", "y"]:
            print("InstructGlobal cancelled")
            return False
        return True
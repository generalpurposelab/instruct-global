import json

class PromptConstructor:
    def __init__(self, output_schema, input_schema, language_code):
        self.output_schema = output_schema
        self.input_schema = input_schema
        self.language_code = language_code
        with open('InstructGlobal/data/prompts.json', 'r') as f:
            self.prompts = json.load(f)

    def construct_prompt(self, category, prompt, csv, batch_size):
        # Fetch the corresponding prompt from prompts.json
        prompt_template = self.prompts[prompt]
        
        if prompt == 'prompt_no_variables':
            new_prompt = prompt_template.format(
                n=batch_size,
                task_category=category,
                task_description=self.output_schema[category]['task_description'],
                target_language=self.language_code,
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
        # print(new_prompt)
        return new_prompt
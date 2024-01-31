import json

class ConstructPrompt:
    def __init__(self):
        with open('InstructGlobal/data/prompts.json', 'r') as f:
            self.prompts = json.load(f)

    def run(self, n, task_category, input_schema_row, output_schema, target_language):
        # print(input_schema_row)
        task_description = output_schema['task_description']
        if task_category == "translation":
            task_description = task_description.replace("from one language to another", f"from English to {target_language} or vice versa")
        av_length = output_schema['av_length']
        length_std = output_schema['length_std']
        num_variables = int(input_schema_row['num_variables'])
        print(input_schema_row)
        
        if input_schema_row.get('complete') == True:
            prompt = self.prompts['prompt_no_variables'].format(n=n, task_category=task_category, task_description=task_description, target_language=target_language, av_length=av_length, length_std=length_std)
        else:
            variable_descriptions = '. '.join([f'Variable_{i} description: {input_schema_row.get(f"variable_{i}_description", "")}' for i in range(1, num_variables + 1)])
            variable_placeholders = ', '.join([f'{{variable_{i}}}' for i in range(1, num_variables + 1) if f'variable_{i}' in input_schema_row])
            if num_variables > 1:
                last_comma = variable_placeholders.rfind(',')
                variable_placeholders = variable_placeholders[:last_comma] + ' and' + variable_placeholders[last_comma + 1:]
            prompt = self.prompts['prompt_variables'].format(n=n, task_category=task_category, num_variables=num_variables, task_description=task_description, dataset_description=input_schema_row.get('description', ""), variable_descriptions=variable_descriptions, variable_placeholders=variable_placeholders)
        # print(prompt)
        return prompt
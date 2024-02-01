from InstructGlobal.main import InstructGlobal

openai_api_key = "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"
model = "gpt-4-turbo-preview" 
target_language = "Yoruba"
language_code = "yo"
input_dir="input"
output_dir="output"
size=50
google_project_id = "global-instruct"

pipeline = InstructGlobal(
    openai_api_key=openai_api_key, # insert openai api key
    target_language=target_language, # target language e.g. Welsh
    language_code=language_code, # insert language code from ISO 639 e.g. Welsh = cy
    model=model, # insert openai model (defaults to gpt-3.5-turbo)
    input_dir=input_dir, # add input directory (defaults to /input)
    output_dir=output_dir, # add output directory (defaults to /output)
    size=size, # add dataset size (defaults to 50000)
    google_project_id=google_project_id # add google project id for translation
)

pipeline.run()
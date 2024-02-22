from InstructGlobal.main import InstructGlobal

openai_api_key = "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" 
model = "gpt-4-turbo-preview" 
target_language = "Yoruba"
language_code = "yo"
input_dir="input"
output_dir="output"
size=100
translation_model = "nllb" 
# google_project_id = ""

pipeline = InstructGlobal(
    openai_api_key=openai_api_key, # insert openai api key
    target_language=target_language, # target language e.g. Welsh
    language_code=language_code, # insert language code from ISO 639 e.g. Welsh = cy
    model=model, # insert openai model (defaults to gpt-3.5-turbo)
    input_dir=input_dir, # add input directory (defaults to /input)
    output_dir=output_dir, # add output directory (defaults to /output)
    size=size, # add dataset size (defaults to 50000)
    translation_model=translation_model, # specify translation_model. currently supports "nllb" for meta's nllb and "google" for google translate (the latter requires a project id and cred.json - see below)
    # google_project_id=google_project_id # optional google project id if google translate is used for translation. if google translate is used, you will also have to add your cred.json file to the root dir
)

pipeline.run()
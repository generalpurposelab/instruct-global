from InstructGlobal.main import InstructGlobal

openai_api_key = "" # openai api key
target_language = "" # target language e.g. Yoruba
language_code = "" # language code from ISO 639 e.g. Yoruba = yo
model = ""  # insert openai model (defaults to gpt-3.5-turbo)
input_dir="input" # input directory (defaults to /input)
output_dir="output" # output directory (defaults to /output)
size=50000 # dataset size (defaults to 50000)
translation_model = "nllb" # specify translation_model. currently supports "nllb" for meta's nllb and "google" for google translate (the latter requires a project id and cred.json - see below)
# google_project_id = "" # google project id if google translate is used for translation. if google translate is used, you will also have to add your cred.json file to the root dir

pipeline = InstructGlobal(
    openai_api_key=openai_api_key, 
    target_language=target_language, 
    language_code=language_code, 
    model=model, 
    input_dir=input_dir, 
    output_dir=output_dir, 
    size=size, 
    translation_model=translation_model, 
    # google_project_id=google_project_id 
)

pipeline.run()

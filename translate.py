import os
from google.cloud import translate

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"

class Translator:
    def __init__(self, project_id: str):
        self.client = translate.TranslationServiceClient()
        self.location = "global"
        self.parent = f"projects/{project_id}/locations/{self.location}"

    def translate_text(self, text: str, language_code: str) -> translate.TranslationServiceClient:
        response = self.client.translate_text(
            request={
                "parent": self.parent,
                "contents": [text],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": "en-US",
                "target_language_code": language_code,
            }
        )

        # Display the translation for each input text provided
        for translation in response.translations:
            print(f"{translation.translated_text}")

        return response

text_to_translate = "Hello, world!"
target_language_code = "yo"
google_project_id = "global-instruct"

translator = Translator(project_id=google_project_id)
translator.translate_text(text=text_to_translate, language_code=target_language_code)
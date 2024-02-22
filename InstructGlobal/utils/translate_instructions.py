import os
import requests
import json
from google.cloud import translate

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"

class Translator:
    def __init__(self, project_id: str, translation_model: str = "google", flores=None):
        self.client = translate.TranslationServiceClient()
        self.location = "global"
        self.parent = f"projects/{project_id}/locations/{self.location}"
        self.project_id = project_id  
        self.translation_model = translation_model
        self.flores = flores or {}

    def translate_text(self, text: str, language_code: str):
        # print(text)
        if not text:  # if text is empty
            return ""

        if self.translation_model == "nllb":
            flores_code = self.flores.get(language_code, language_code)
            return self.translate_text_nllb(text, flores_code)
        elif self.translation_model == "google":
            return self.translate_text_google(text, language_code)
        else:
            raise ValueError(f"Unsupported translation model: {self.translation_model}")

    def translate_text_google(self, text: str, language_code: str):
        if not self.project_id:
            raise ValueError("Google project ID is required for Google Translate.")
        try:
            response = self.client.translate_text(
                request={
                    "parent": self.parent,
                    "contents": [text],
                    "mime_type": "text/plain",
                    "source_language_code": "en-US",
                    "target_language_code": language_code,
                }
            )
            return response
        except Exception as e:
            # print(f"An error occurred during translation: {e}")
            return ""

    def preprocess_text(self, text: str) -> str:
        # Strip leading and trailing quotation marks and whitespace
        text = text.strip('"').strip()
        # Replace newline characters with spaces
        text = text.replace('\n', ' ')
        return text

    def translate_text_nllb(self, text: str, flores_code: str):
        # Preprocess the text
        text = self.preprocess_text(text)
        url = 'https://winstxnhdw-nllb-api.hf.space/api/v2/translate'
        headers = {'Content-Type': 'application/json'}
        data = {
            "text": text,
            "source": "eng_Latn",
            "target": flores_code
        }
        print(data)

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = response.json()
            print(response_data)
            return response_data[0]['translatedText']
        except Exception as e:
            return ""

    def translate_instructions(self, instructions, language_code):
        translated_instructions = []

        for instruction in instructions:
            print(instruction)
            translated_instruction = self.translate_text(instruction['instruction_en'], language_code)
            translated_input = self.translate_text(instruction['input_en'], language_code)
            translated_output = self.translate_text(instruction['output_en'], language_code)

            if not isinstance(translated_instruction, str):
                translated_instruction = translated_instruction.translations[0].translated_text
            if not isinstance(translated_input, str):
                translated_input = translated_input.translations[0].translated_text
            if not isinstance(translated_output, str):
                translated_output = translated_output.translations[0].translated_text

            translated_instructions.append({
                f'instruction_{language_code}': translated_instruction,
                f'input_{language_code}': translated_input,
                f'output_{language_code}': translated_output,
            })

        return translated_instructions
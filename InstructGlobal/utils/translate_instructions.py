import os
import re
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
        if not text:
            return ""

        print("Before translation:", text)
        placeholders = {}
        placeholder_pattern = r'\{[^}]*\}'
        original_placeholders = []

        # Capture placeholders and store them in a list
        def capture_placeholders(match):
            original_placeholder = match.group(0)
            original_placeholders.append(original_placeholder)
            return original_placeholder

        # Apply the capturing function to find all placeholders
        re.sub(placeholder_pattern, capture_placeholders, text)

        # Proceed with translation
        if self.translation_model == "nllb":
            flores_code = self.flores.get(language_code, language_code)
            translated_text = self.translate_text_nllb(text, flores_code)
        elif self.translation_model == "google":
            translated_text = self.translate_text_google(text, language_code)
        else:
            raise ValueError(f"Unsupported translation model: {self.translation_model}")

        # Function to replace translated placeholders with original placeholders
        def replace_translated_placeholders(match):
            if original_placeholders:
                # Pop the first original placeholder from the list and return it
                return original_placeholders.pop(0)
            else:
                return match.group(0)  # If no original placeholders left, return the match itself

        # Replace any structure that matches a placeholder pattern in the translated text
        translated_text = re.sub(placeholder_pattern, replace_translated_placeholders, translated_text)

        print("After translation:", translated_text)
        return translated_text

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
        # print(data)

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            # print("Response Text:", response.text)
            translated_text = response.text.strip()
            return translated_text
        except Exception as e:
            # print(f"An error occurred: {e}")
            return ""

    def translate_instructions(self, instructions, language_code):
        translated_instructions = []

        for instruction in instructions:
            # print(instruction)
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

        # print("translate_instructions:", translated_instructions)
        return translated_instructions
import os
from google.cloud import translate

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"

class Translator:
    def __init__(self, project_id: str):
        self.client = translate.TranslationServiceClient()
        self.location = "global"
        self.parent = f"projects/{project_id}/locations/{self.location}"

    def translate_text(self, text: str, language_code: str) -> translate.TranslationServiceClient:
        if not text:  # if text is empty
            return ""

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

    def translate_instructions(self, instructions, language_code):
        translated_instructions = []

        for instruction in instructions:
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
# accepts FLORES codes at https://github.com/facebookresearch/flores/blob/main/flores200/README.md

import requests
import json

url = 'https://winstxnhdw-nllb-api.hf.space/api/v2/translate'
headers = {'Content-Type': 'application/json'}
data = {
    "text": "What is the sentiment of this Tweet: {variable_1}",
    "source": "eng_Latn",
    "target": "yor_Latn"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.text)
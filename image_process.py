import base64
import requests
from openai import OpenAI

# OpenAI API Key (use environment variable for security)
api_key = "sk-EJ5WHbYPpXuEpqqX3DOWzUDobxAT3Z6fYfUQHM87_DT3BlbkFJOMIbnG9h61jLZF1Ju3DCauH3oeUhl1LqPKaGHgZq4A"
client = OpenAI(api_key=api_key)

# Encode image in Base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Process uploaded image to generate metadata
def image_process(image_path):
    queries = [
        "Provide a caption for this image in fewer than 10 words.",
        "Provide 10 tags for this image in CSV format.",
        "Provide a short description for this image."
    ]

    base64_image = encode_image(image_path)
    metadata = []

    for query in queries:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 100
        }

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            metadata.append(response.json()["choices"][0]["message"]["content"])
        else:
            metadata.append("Error generating response")

    return metadata  # Returns [caption, tags, description]

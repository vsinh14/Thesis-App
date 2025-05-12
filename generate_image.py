import time
import os
import shutil
import wget
from openai import OpenAI
from database import database
from image_process import image_process
import base64
import requests

# OpenAI API Key (Use environment variable for security)
api_key = "sk-EJ5WHbYPpXuEpqqX3DOWzUDobxAT3Z6fYfUQHM87_DT3BlbkFJOMIbnG9h61jLZF1Ju3DCauH3oeUhl1LqPKaGHgZq4A"
client = OpenAI(api_key=api_key)

# Folders
GENERATED_FOLDER = "static/images/generated_images"
ARCHIVE_FOLDER = "archive"

# Ensure folders exist
os.makedirs(GENERATED_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

# Move old images to archive
def archive_old_images():
    for file in os.listdir(GENERATED_FOLDER):
        file_path = os.path.join(GENERATED_FOLDER, file)
        if os.path.isfile(file_path) and file.startswith("generated_"):
            try:
                shutil.move(file_path, os.path.join(ARCHIVE_FOLDER, file))
                print(f"Moved old image to archive: {file}")
            except Exception as e:
                print(f"Error moving {file} to archive: {str(e)}")

def generate_image_from_openai(prompt):
    """
    Generates an image using OpenAI's API based on the provided prompt.
    Returns the image URL if successful, or None if not.
    """
    try:
        response = client.images.generate(
          model="dall-e-3",
          prompt=prompt,
          size="1024x1024",
          quality="standard",
          n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print("Error generating image:", e)
        return None

def generate_and_process_image(prompt):
    """
    Archives old images, generates a new image using the OpenAI API, downloads it,
    and returns the filename of the generated image.
    """
    response = generate_image_from_openai(prompt)

    image_filename = os.path.join(GENERATED_FOLDER, f"generated_{int(time.time())}.png")
    try:
        wget.download(response, image_filename)
        print(f"\nGenerated new image at {image_filename}")
        return image_filename
    except Exception as e:
        print("Error downloading image:", e)
        return None

if __name__ == "__main__":
    # Example prompt; modify as needed.
    prompt = "A futuristic cityscape at sunset"
    generate_and_process_image(prompt)

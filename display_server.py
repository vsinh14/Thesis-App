import os
import time
import threading
from openai import OpenAI
from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
import glob
from database import database  # Assuming Database class for inserting metadata and querying it
import wget
from PIL import Image  # To simulate image generation (you can replace this with actual image generation logic)

app = Flask(__name__)

# Folder where images are stored
IMAGE_FOLDER = "static/images/generated_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)
api_key = "sk-EJ5WHbYPpXuEpqqX3DOWzUDobxAT3Z6fYfUQHM87_DT3BlbkFJOMIbnG9h61jLZF1Ju3DCauH3oeUhl1LqPKaGHgZq4A"
client = OpenAI(api_key=api_key)

# Function to check if uploads are enabled by reading 'enabled.txt'
def is_upload_enabled():
    """Check if the uploads are enabled by reading 'enabled.txt'."""
    try:
        with open('enabled.txt', 'r') as file:
            status = file.read().strip()  # Read the file and strip any extra spaces/newlines
            return status == "enabled"
    except FileNotFoundError:
        return False  # If the file doesn't exist, assume uploads are disabled

def get_latest_images(num_images=3):
    """Returns the latest 'num_images' files from the folder."""
    list_of_files = glob.glob(os.path.join(IMAGE_FOLDER, '*'))
    if not list_of_files:
        return []  # No images found
    
    # Sort files by creation time (most recent first)
    list_of_files.sort(key=os.path.getctime, reverse=True)
    
    # Get the specified number of most recent files
    return [os.path.basename(f) for f in list_of_files[:num_images]]

def generate_images(tags, num_images=3):
    """Dummy function to simulate generating images from tags."""
    generated_images = []
    for _ in range(num_images):
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))  # Placeholder image generation
        generated_images.append(img)  # Append dummy image
    return generated_images

@app.route('/')
def home():
    latest_images = get_latest_images()  # Get the top 3 latest images

    # Fetch tags for each image from the database
    images_with_tags = []
    for image in latest_images:
        tags = database.db_select_tags(image)  # Fetch tags for the image
        images_with_tags.append({'image': image, 'tags': tags})
    
    return render_template('index.html', images_with_tags=images_with_tags)

@app.route('/start_timer', methods=['POST'])
def start_timer():
    """Writes 'enabled' to enabled.txt when the timer starts."""
    with open("enabled.txt", "w") as file:
        file.write("enabled")
    return jsonify({"status": "enabled"})

@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    """Writes 'disabled' to enabled.txt when the timer ends."""
    with open("enabled.txt", "w") as file:
        file.write("disabled")

    # Start image generation after the timer ends
    generate_new_images()

    return jsonify({"status": "disabled"})

def generate_new_images():
    """Generate new images using tags from the recently uploaded images."""
    # Get images uploaded in the last 2 minutes (120 seconds)
    recent_images = database.db_select_recent(120)
    if not recent_images:
        print("No recent images found to generate new ones.")
        return
    
    # Extract tags from the recent images
    all_tags = ""
    print(recent_images)
    for tags in recent_images:
        csvValues = tags[0].split("\n")
        all_tags = all_tags + csvValues[3] + ", "
        print(all_tags)

    # Generate 3 new images using the extracted tags
    makeImage(all_tags, num_images=3)

    print("3 new images generated successfully!")

def makeImage(tags, num_images=3):
    print(tags)
    directoryList = os.listdir(IMAGE_FOLDER)
    counter = 0
    for i in directoryList:
        name = i.split("_")
        if(name[0] == "genimg"):
            counter +=1
    for _ in range(num_images):
        fileName = "genimg_" + str(counter) + ".png" 
        response = client.images.generate(
            model="dall-e-3",
            prompt=tags,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        wget.download(response.data[0].url,IMAGE_FOLDER + "/" + fileName)
        counter += 1

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

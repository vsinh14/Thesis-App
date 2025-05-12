from flask import Flask, render_template
import os
import glob
from database import database  # Import the Database class to fetch image tags

app = Flask(__name__)

# Folder where images are stored
IMAGE_FOLDER = "static/images/generated_images"

def get_latest_images(num_images=3):
    """Returns the latest 'num_images' files from the folder."""
    list_of_files = glob.glob(os.path.join(IMAGE_FOLDER, '*'))
    if not list_of_files:
        return []  # No images found
    
    # Sort files by creation time (most recent first)
    list_of_files.sort(key=os.path.getctime, reverse=True)
    
    # Get the specified number of most recent files
    return [os.path.basename(f) for f in list_of_files[:num_images]]

@app.route('/')
def home():
    latest_images = get_latest_images()  # Get the top 3 latest images

    # Fetch tags for each image from the database
    images_with_tags = []
    for image in latest_images:
        print(image)
        tags = database.db_select_tags(image)  # Fetch tags for the image
        images_with_tags.append({'image': image, 'tags': tags})
    
    return render_template('index.html', images_with_tags=images_with_tags)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

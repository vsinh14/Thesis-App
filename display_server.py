from flask import Flask, render_template
import os
import glob

app = Flask(__name__)

# Folder where images are stored
IMAGE_FOLDER = "static/images/generated_images"

def get_latest_image():
    """Returns the latest image file from the folder."""
    list_of_files = glob.glob(os.path.join(IMAGE_FOLDER, '*'))
    print(list_of_files)
    if not list_of_files:
        return None  # No image found
    latest_file = max(list_of_files, key=os.path.getctime)  # Get most recently created file
    return os.path.basename(latest_file)  # Return just the filename

@app.route('/')
def home():
    latest_image = get_latest_image()
    return render_template('index.html', latest_image=latest_image)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


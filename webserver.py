import os
import time
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from generate_image import generate_and_process_image# Import your image generation function
from database import database
import shutil  # To move old images
from image_process import image_process  # Import the function to process the image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated_images'
ARCHIVE_FOLDER = 'archive'

# Ensure necessary folders exist
for folder in [UPLOAD_FOLDER, GENERATED_FOLDER, ARCHIVE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to upload images
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        
        if file and allowed_file(file.filename):
            # Save the uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the image to extract tags using image_process.py
            imageData = image_process(file_path)  # Assuming this function returns the tags for the image
            
            # Insert the image metadata into the database
            image_name = filename
            caption = imageData[0] 
            description = imageData[2] 
            tags = imageData[1] 

            timestamp = int(time.time())  # Current timestamp
            
            # Insert metadata into the database
            database.db_insert(image_name, caption, tags, description, timestamp)
            
            return f"File uploaded successfully! View it <a href='/uploads/{filename}'>here</a>."
    
    return '''
    <!doctype html>
    <title>Upload Image</title>
    <h1>Upload an Image</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

# Route to serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# Function to archive old images and generate a new one

def scheduled_task():
    print("Running scheduled task...")

    # Move old images to the archive folder
    for file in os.listdir(GENERATED_FOLDER):
        old_path = os.path.join(GENERATED_FOLDER, file)
        new_path = os.path.join(ARCHIVE_FOLDER, file)
        shutil.move(old_path, new_path)
        print(f"Moved old image to archive: {file}")

    prompt = database.db_select_recent()
    promptString = ""
    setList = [] 
    for i in prompt[0]:
        xList = i.split("```")
        keys = xList[1].split(',')
        for i in keys:
            iden = i.replace('"','')
            noNew = iden.replace("\n",'')
            value = noNew.replace(" ",'')
            setList.append(value)
    setValues = set(setList)

    for i in setValues:
        if len(promptString) == 0:
            promptString = promptString + i
        promptString = promptString + "," + i
        
    # Generate a new image
    new_image_url = generate_and_process_image(promptString)

    # Save new image
    new_image_path = os.path.join(GENERATED_FOLDER, "latest_generated.png")
    os.system(f"wget -O {new_image_path} {new_image_url}")
    print("Generated and saved new image!")

# Start scheduler to run every 24 hours
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'interval', minutes=1)
scheduler.start()

# Run Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)


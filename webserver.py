import os
import time
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from image_process import image_process  # Function to process the image
from database import database

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            tags = imageData[0] 

            timestamp = int(time.time())  # Current timestamp
            
            # Insert metadata into the database
            database.db_insert(image_name, tags, timestamp)
            
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

# Run Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)


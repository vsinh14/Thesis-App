from flask import Flask, request, render_template, flash, redirect
import os
import time
from werkzeug.utils import secure_filename
from image_process import image_process  # Function to process the image
from database import database  # Assuming the Database class for inserting metadata

app = Flask(__name__)

# Define upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SECRET_KEY'] = 'your_secret_key_here'  # For flash messages

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to check if uploads are enabled by reading 'enabled.txt'
def is_upload_enabled():
    """Check if the uploads are enabled by reading 'enabled.txt'."""
    try:
        with open('enabled.txt', 'r') as file:
            status = file.read().strip()  # Read the file and strip any extra spaces/newlines
            return status == "enabled"
    except FileNotFoundError:
        return False  # If the file doesn't exist, assume uploads are disabled

# Route to upload images
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    upload_enabled = is_upload_enabled()  # Check if uploads are enabled
    if not upload_enabled:
        flash("Uploads are currently disabled. Please try again later.", "danger")
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash("No selected file", "danger")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save the uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the image to extract tags using image_process.py
            imageData = image_process(file_path)  # Assuming this function returns the tags for the image
            
            # Insert the image metadata into the database
            image_name = filename
            tags = imageData[0]  # Assuming the tags are at index 0

            timestamp = int(time.time())  # Current timestamp
            
            # Insert metadata into the database
            database.db_insert(image_name, tags, timestamp)
            
            flash(f"File '{filename}' uploaded successfully!", "success")
            return f"File uploaded successfully! View it <a href='/uploads/{filename}'>here</a>."
    
    return render_template('upload.html', upload_enabled=upload_enabled)

# Run Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)


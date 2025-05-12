import base64
import io
import openai
from PIL import Image

# OpenAI API Key (use environment variable for security)
api_key = "sk-EJ5WHbYPpXuEpqqX3DOWzUDobxAT3Z6fYfUQHM87_DT3BlbkFJOMIbnG9h61jLZF1Ju3DCauH3oeUhl1LqPKaGHgZq4A"
openai.api_key = api_key 

MAX_WIDTH = 800  # Maximum width in pixels
MAX_TOKENS = 100  # Maximum tokens for response

def resize_and_compress_image(image_path, max_width=800):
    """
    Resizes the image proportionally based on its original size, to avoid excessive token usage.
    Args:
        image_path (str): Path to the image file.
        max_width (int): Maximum width for the resized image (default 800px).
    Returns:
        str: Base64-encoded resized and compressed image.
    """
    # Open the image file
    img = Image.open(image_path)

    # Get the original dimensions
    original_width, original_height = img.size

    # Calculate the aspect ratio and resize the image proportionally
    aspect_ratio = original_height / original_width
    target_width = min(original_width, max_width)
    target_height = int(target_width * aspect_ratio)

    # Resize the image using LANCZOS resampling (equivalent to ANTIALIAS)
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Compress the image and save it to a BytesIO object (JPEG format for compression)
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format="JPEG", quality=25)  # Adjust quality for better compression

    # Convert the image to base64
    img_byte_array.seek(0)
    compressed_base64_image = base64.b64encode(img_byte_array.read()).decode("utf-8")

    return compressed_base64_image

# Your image processing function
def image_process(image_path):
    # Prepare the image query for OpenAI API
    queries = [
        "Provide 10 tags for this image in CSV format.",
    ]
    
    # Encode the image to base64 (if needed for processing)
    compressed_base64_image = resize_and_compress_image(image_path)
    
    metadata = []
    for query in queries:
        # Prepare the message and prompt for OpenAI
        prompt = f"{query}\nImage: {compressed_base64_image}"

        # Construct the payload for the OpenAI API
        payload = {
            "model": "gpt-4o-mini",  
            "prompt": prompt,  # 'prompt' should be a string, not a list of dicts
            "max_tokens": MAX_TOKENS# Optional: Set the maximum tokens for the response
        }

        # Correct way to call OpenAI's API for completions
        try:
            response = openai.Completion.create(**payload)  # Use the correct method for completions
            metadata.append(response['choices'][0]['text'].strip())  # Get the response text
        except Exception as e:
            print(f"Error generating image data: {e}")

    # Ensure that the metadata list is not empty
    if len(metadata) == 0:
        print("Error: No metadata generated.")
        return []
    return metadata

# Encode the image into base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


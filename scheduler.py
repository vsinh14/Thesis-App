import schedule
import time
import os

def run_image_generation():
    print("Running image generation script...")
    os.system("python generate_image.py")  # Runs the image generation script

# Schedule the task to run every 3 days
schedule.every(3).days.do(run_image_generation)

if __name__ == "__main__":
    print("Scheduler started... Image generation will run every 3 days.")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute



import cv2
from pathlib import Path
import hashlib
import google.generativeai as genai
import time
import certifi
import pymongo

import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, message, to_email, from_email, password, smtp_server='smtp.gmail.com', smtp_port=587):
    # Create a MIME multipart message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the message to the email
    msg.attach(MIMEText(message, 'plain'))

    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Start TLS encryption

    # Log in to the SMTP server
    server.login(from_email, password)

    # Send the email
    server.sendmail(from_email, to_email, msg.as_string())

    # Quit the SMTP server
    server.quit()

# Example usage
subject = "Test Email"
message = "you got mail!."
to_email = "recipient@example.com"
from_email = "your_email@gmail.com"
password = "your_password"

client = pymongo.MongoClient("mongodb+srv://james:yR2Vrki1VlZTzVRJ@cluster0.cuvnbxl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", tlsCAFile=certifi.where())

db = client.test
collection = db.exercises
testemail = "jameslodgemath@gmail.com"


def print_collection_data(data):
    try:
        # Retrieve data from MongoDB Atlas
        cursor = collection.find()
        # Print data
        print(cursor)
        for document in cursor:
            myquery = { "description": document["description"] }
            newvalues = { "$set": { "description": document["description"] + data } }
            print(document)
            global email = document["username"]
            collection.update_one(myquery, newvalues)

    except Exception as e:
        print("An error occurred:", e)



responses = []
# Function to configure Gemini API
def configure_gemini():
    genai.configure(api_key="AIzaSyCB70qDdA6iPE8jxwkPZSRhmPYbfcKSBfA")

# Function to capture an image using OpenCV
def capture_image():
    # Access the default camera (usually the webcam)
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return None

    # Capture a frame
    ret, frame = cap.read()

    # Release the camera
    cap.release()

    # Check if the frame is captured successfully
    if not ret:
        print("Error: Could not capture frame")
        return None

    return frame

# Function to upload an image to Gemini
def upload_image(image):
    # Save the captured image
    image_path = "captured_image.png"
    cv2.imwrite(image_path, image)

    # Calculate hash for the image
    hash_id = hashlib.sha256(Path(image_path).read_bytes()).hexdigest()

    # Upload the image to Gemini
    uploaded_file = genai.upload_file(path=image_path, display_name=hash_id)
    
    return uploaded_file

# Function to delete an uploaded file from Gemini
def delete_uploaded_file(uploaded_file):
    genai.delete_file(name=uploaded_file.name)

# Function to continuously process frames
def process_frames():
    while True:
        # Capture an image using OpenCV
        captured_image = capture_image()

        # Check if an image is captured
        if captured_image is not None:
            print("calling model . . .")
            # Upload the image to Gemini
            uploaded_file = upload_image(captured_image)
            
            # Generate content using Gemini
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time
            prompt_parts = [
                uploaded_file,
                f"Based on the image of the flyer, write a summary only about the current date and time ({current_datetime}), then separated by a comma find the name of the sender, then separated by a comma, the topic or subject of the mail, then separated by a comma, a summary of the information, then separated by a comma, determine if the mail is important or spam. An example, following the exact format, is 'date, sender, subject, summary, not important or important', if you dont see a flyer or mail return 'none'"
            ]
            response = model.generate_content(prompt_parts)
            firdocument = collection.find_one({"_id": "66364d64fb3872a7823cc815"})

            # Delete the uploaded image
            delete_uploaded_file(uploaded_file)
            print()
            if "Netflix".lower() in response.text.lower() or "none".lower() in response.text.lower() or "System Administrator".lower() in response.text.lower():
                print("netflix. . .")
                text = "DON'T UPDATE"
            else:
                text = response.text
                print("updating data . . .")
                nextxt = "," + response.text
                print(nextxt)
                print_collection_data(nextxt)
                if email[-1].lower() == "important":
                    send_email(subject, message, to_email, from_email, password)

        else:
            print("Error: Failed to capture image")

        # Introduce a delay before capturing the next frame
        print("hi")
        time.sleep(3)  # Adjust the delay as needed





# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

# Create a Gemini model
model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Configure Gemini API
configure_gemini()

# Start processing frames
process_frames()

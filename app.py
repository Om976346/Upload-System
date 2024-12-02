import os
import time
import requests
from flask import Flask, request, render_template, jsonify, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the bot token and chat ID from .env file
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Allowed file types
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpg', 'png', 'docx', 'zip', 'rar', 'mp3', 'mp4'}

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Used to store the uploaded filenames in session

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure the file has a valid extension
def ensure_extension(file):
    if not allowed_file(file.filename):
        raise ValueError("Invalid file type!")
    file.filename = secure_filename(file.filename)  # Sanitize filename
    return file

# Route: Home (Upload Page)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Handle multiple file uploads
        files = request.files.getlist("file")
        uploaded_files = []

        for file in files:
            try:
                if file and allowed_file(file.filename):
                    file = ensure_extension(file)
                    
                    # Send the file to Telegram without saving locally
                    file.seek(0)
                    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'
                    payload = {'chat_id': CHAT_ID, 'caption': f"New file uploaded: {file.filename}"}
                    files_data = {'document': (file.filename, file.stream, file.mimetype)}

                    response = requests.post(url, data=payload, files=files_data, timeout=120)

                    if response.status_code == 200:
                        uploaded_files.append(file.filename)
                    else:
                        print(f"Error from Telegram API: {response.json()}")
                        return jsonify({"error": f"Failed to send file {file.filename} to Telegram!"}), 500

                    time.sleep(1)  # Avoid Telegram API rate limits
                else:
                    return jsonify({"error": "Invalid file type!"}), 400

            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"Error uploading {file.filename}: {str(e)}"}), 500

        # Store the filenames in session for display
        if uploaded_files:
            if 'uploaded_files' not in session:
                session['uploaded_files'] = []
            session['uploaded_files'].extend(uploaded_files)

            return jsonify({"success": f"Files uploaded and sent to Telegram: {', '.join(uploaded_files)}"})

        return jsonify({"error": "No valid files uploaded!"}), 400

    # Render the HTML template
    uploaded_files = session.get('uploaded_files', [])
    return render_template("index.html", uploaded_files=uploaded_files)

# Route: List Uploaded Files
@app.route("/files", methods=["GET"])
def list_files():
    uploaded_files = session.get('uploaded_files', [])
    return jsonify(uploaded_files)

if __name__ == "__main__":
    app.run(debug=True)

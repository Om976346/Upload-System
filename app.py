import os
import time
import logging
import requests
from flask import Flask, request, render_template, jsonify, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram bot credentials
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpg', 'png', 'docx', 'zip', 'rar', 'mp3', 'mp4'}

# Flask app configuration
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Validate file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure file is valid and has a secure name
def ensure_file(file):
    if not allowed_file(file.filename):
        raise ValueError("Invalid file type!")
    file.filename = secure_filename(file.filename)
    return file

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        files = request.files.getlist("file")
        uploaded_files = []

        for file in files:
            try:
                # Validate and secure the file
                if file and allowed_file(file.filename):
                    file = ensure_file(file)

                    # Upload to Telegram
                    file.seek(0)  # Reset file pointer
                    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'
                    payload = {'chat_id': CHAT_ID, 'caption': f"New file uploaded: {file.filename}"}
                    files_data = {'document': (file.filename, file.stream, file.mimetype)}

                    response = requests.post(url, data=payload, files=files_data, timeout=120)

                    if response.status_code == 200:
                        uploaded_files.append(file.filename)
                    else:
                        logging.error(f"Telegram API error for {file.filename}: {response.text}")
                        return jsonify({"error": f"Failed to send file '{file.filename}' to Telegram. Response: {response.text}"}), 500

                    time.sleep(1)  # Prevent API rate limit issues

                else:
                    return jsonify({"error": f"Invalid file type: {file.filename}"}), 400

            except ValueError as e:
                logging.error(f"Validation error: {str(e)}")
                return jsonify({"error": str(e)}), 400

            except requests.exceptions.RequestException as e:
                logging.error(f"Request error: {str(e)}")
                return jsonify({"error": f"Failed to upload '{file.filename}': {str(e)}"}), 500

        if uploaded_files:
            if 'uploaded_files' not in session:
                session['uploaded_files'] = []
            session['uploaded_files'].extend(uploaded_files)

            return jsonify({"success": f"Uploaded files: {', '.join(uploaded_files)}"})

        return jsonify({"error": "No valid files to upload."}), 400

    uploaded_files = session.get('uploaded_files', [])
    return render_template("index.html", uploaded_files=uploaded_files)

@app.route("/files", methods=["GET"])
def list_files():
    uploaded_files = session.get('uploaded_files', [])
    return jsonify(uploaded_files)

if __name__ == "__main__":
    app.run(debug=True)

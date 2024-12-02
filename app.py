import os
from flask import Flask, request, render_template, jsonify, session
import requests
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

# Route: Home (Upload Page)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Handle multiple file upload
        files = request.files.getlist("file")
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Send the file to Telegram without saving it locally
                file.seek(0)  # Ensure the file pointer is at the start
                url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'
                payload = {'chat_id': CHAT_ID, 'caption': f"New file uploaded: {file.filename}"}
                files_data = {'document': file}
                response = requests.post(url, data=payload, files=files_data)

                if response.status_code == 200:
                    uploaded_files.append(file.filename)
                else:
                    return jsonify({"error": f"Failed to send file {file.filename} to Telegram!"}), 500

        if uploaded_files:
            # Store the filenames in session to display them later
            if 'uploaded_files' not in session:
                session['uploaded_files'] = []
            session['uploaded_files'].extend(uploaded_files)

            return jsonify({"success": f"Files uploaded and sent to Telegram: {', '.join(uploaded_files)}"})

        return jsonify({"error": "Invalid file types!"}), 400

    # Render the HTML template with the list of uploaded files
    uploaded_files = session.get('uploaded_files', [])
    return render_templates("index.html", uploaded_files=uploaded_files)

# Route: List Uploaded Files
@app.route("/files", methods=["GET"])
def list_files():
    # Display uploaded file names stored in the session
    uploaded_files = session.get('uploaded_files', [])
    return jsonify(uploaded_files)

if __name__ == "__main__":
    app.run(debug=True)

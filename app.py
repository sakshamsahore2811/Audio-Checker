# Audio checking app interface built using Flask by Saksham Sharma (sakshamsahore@gmail.com)

# Used flask for backend, SQLAlchemy for managing database with SQLite database, mutagen for handling mp3 audio file duration and pydub for other extentions

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
from mutagen.mp3 import MP3
from pydub import AudioSegment
from mutagen.mp3 import HeaderNotFoundError
from pydub.exceptions import CouldntDecodeError

# Initializing a SQLite database for storing audio file name, extension, date and time of upload
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///audio_files.db'
db = SQLAlchemy(app) # Creating database as db 
app.app_context().push()

# Creating the database model for aduio_files.db with following columns
class AudioFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False) # Cannot contain null value
    extension = db.Column(db.String(10), nullable=False) # Cannot contain null value
    upload_date = db.Column(db.DateTime, default=datetime.datetime.utcnow) # Automatically stores the universal time coordinates of the time and date of upload

# To check if the length of the audio files exceeds 10 minutes, creating a function using mutagen library
def get_audio_duration(audio_path, extension):
    try:
        # For mp3 extension files
        if extension.lower() == '.mp3':
            audio = MP3(audio_path)
            audio_duration = datetime.timedelta(seconds=audio.info.length)
        # For other extension files
        else:
            audio = AudioSegment.from_file(audio_path)
            audio_duration = datetime.timedelta(milliseconds=len(audio))
        
        return audio_duration
    except (HeaderNotFoundError, CouldntDecodeError):
        raise Exception("Error reading audio file")
    
# Home page route to allow user to upload single or multiple audio files 
# and show the uploaded files in the database in a tabular form
@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('audioFiles')
        # Iterating through the files in case there are multiple files uploaded
        for uploaded_file in uploaded_files:
            # The file has to have a name
            if uploaded_file.filename != '':
                filename = uploaded_file.filename
                extension = os.path.splitext(filename)[1]
                # Upload the file into the static/uploads folder
                audio_path = os.path.join('static/uploads', filename)
                uploaded_file.save(audio_path)
                # Handle the warning for the case if file length exceeds 10 minutes
                try:
                    audio_duration = get_audio_duration(audio_path, extension)
                    if audio_duration <= datetime.timedelta(minutes=10):
                        new_audio = AudioFile(filename=filename, extension=extension)
                        db.session.add(new_audio)
                        db.session.commit()
                    else:
                        new_audio = AudioFile(filename=filename, extension=extension)
                        db.session.add(new_audio)
                        db.session.commit()
                        error_message = "Warning : Audio duration exceeds 10 minutes"
                        return render_template('upload.html',error_message=error_message,files=files)
                except Exception:
                    pass
        
        files = AudioFile.query.all()
        return render_template('upload.html', files=files)
    
    files = AudioFile.query.all()
    return render_template('upload.html', files=files)

# Running the app
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

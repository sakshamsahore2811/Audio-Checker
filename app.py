# Audio checking app interface built using Flask by Saksham Sharma (sakshamsahore@gmail.com)

""" 
Used flask API for backend, SQLAlchemy for managing database with SQLite database, 
mutagen for handling mp3 audio file duration and pydub for other extentions of files.
A tabular representation of the uploaded audio files is shown along with other details such as 
date and time, name, id and extension.
"""

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
from mutagen.mp3 import MP3
from pydub import AudioSegment
from mutagen.mp3 import HeaderNotFoundError
from pydub.exceptions import CouldntDecodeError

app = Flask(__name__)

# Initializing a SQLite database for storing audio file name, extension, date and time of upload
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///audio_files.db'
db = SQLAlchemy(app) # Creating database as db 
app.app_context().push() # push a context manually since you have direct access to the app 

# Creating the database model for aduio_files.db with following columns
class AudioFile(db.Model):
    id = db.Column(db.Integer, primary_key=True) # unique key for every audio file 
    filename = db.Column(db.String(255), nullable=False) # Audio file name, Cannot contain null value
    extension = db.Column(db.String(10), nullable=False) # Extension type, Cannot contain null value
    upload_date = db.Column(db.DateTime, default=datetime.datetime.utcnow) # Automatically stores the universal time coordinates of the time and date of upload

# To check if the length of the audio files exceeds 10 minutes, creating a function using mutagen library
def get_audio_duration(audio_path, extension):
    try:
        # if the file type in .mp3
        if extension.lower() == '.mp3':
            audio = MP3(audio_path)
            audio_duration = datetime.timedelta(seconds=audio.info.length)
        # any other file type
        else:
            audio = AudioSegment.from_file(audio_path)
            audio_duration = datetime.timedelta(milliseconds=len(audio))
        
        return audio_duration
    # Handling exception
    except (HeaderNotFoundError, CouldntDecodeError):
        raise Exception("Error reading audio file")

"""
Home page route to allow user to upload single or multiple audio files 
and show the uploaded files in the database in a tabular form
"""
@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('audioFiles')
        # Iterating through the files in case mulitple files are uploaded
        for uploaded_file in uploaded_files:
            if uploaded_file.filename != '':
                filename = uploaded_file.filename
                extension = os.path.splitext(filename)[1]
                
                # Adding the filename and extension to the database
                new_audio = AudioFile(filename=filename, extension=extension)
                db.session.add(new_audio)
                db.session.commit()
                
                # Storing the audio files in static/uploads folder
                upload_path = os.path.join('static/uploads', filename)
                uploaded_file.save(upload_path)
                
                # Handling the exception 
                try:
                    audio_duration = get_audio_duration(upload_path, extension)  # Pass the extension here
                    if audio_duration > datetime.timedelta(minutes=10):
                        error_message = "Audio duration exceeds 10 minutes"
                        return render_template('upload.html', error_message=error_message)
                except Exception:
                    error_message = "Error reading audio file"
                    return render_template('upload.html', error_message=error_message)
        
        files = AudioFile.query.all()
        return render_template('upload.html', files=files)
    
    files = AudioFile.query.all()
    return render_template('upload.html', files=files)


# Running the app
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from file_alchemy import FileManager, Base64ImageAttach

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'UPLOAD_FOLDER'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)
filemanager = FileManager(app, db)

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    avatar = Column(String, nullable=True) # Column will store path to image file

avatar_file = filemanager.attach_field(
    Base64ImageAttach(
        column=User.avatar, # attached column *Required
        filename_generator=User.username, # file name generator column must be unique! *Required
        prefix='/avatars', # prefix in file path must be unique at table *Required
        size=(400, 400) # image size width x height *Optional
    )
)

with app.app_context():
    db.drop_all()
    db.create_all()

from flask import send_from_directory

@app.get('/UPLOAD_FOLDER/<path>')
def get_files(path):
    return send_from_directory(filemanager.upload_folder or app.config['UPLOAD_FOLDER'], path=path)


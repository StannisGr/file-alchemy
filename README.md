# File-Alchemy
<a target="new" href="https://pypi.python.org/pypi/file-alchemy"><img border=0 src="https://img.shields.io/badge/python-3.10+-blue.svg?style=flat" alt="Python version"></a>
<a target="new" href="https://pypi.python.org/pypi/file-alchemy">
<img border=0 src="https://img.shields.io/pypi/v/file-alchemy.svg?maxAge=60%" alt="PyPi version">
</a>
<br/>
At the moment, the library can only work correctly on the Flask framework platform.
## Quick start

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from file_alchemy import FileManager, Base64ImageAttach

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['UPLOAD_FOLDER'] = 'UPLOAD_FOLDER'
db = SQLAlchemy(app)
filemanager = FileManager(app, db)


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, unique=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True) # Column will store path to image file

# Register file attachment 
"""
    Path generated:
 {app.config["UPLOAD_FOLDER"]}/{Base64ImageAttach.__name__}/{Model.__tablename__}/{prefix}
"""
avatar_file = filemanager.attach_field(
    Base64ImageAttach(
        column=User.avatar, # attached column *Required
        filename_generator=User.username, # file name generator column must be unique! *Required
        prefix='/avatars', # prefix in file path must be unique for table *Required
        size=(400, 400) # image size width x height *Optional
    )
)
""" 
    Base64ImageAttach responsible for adding, deleting, updating the image and its title, while inserting, deleteing, updating rows in table.
    Base64ImageAttach is waiting base64 image format to set in attached column - https://en.wikipedia.org/wiki/Base64 
"""

with app.app_context():
    db.drop_all()
    db.create_all()

# Get uploaded files
from flask import send_from_directory

@app.get('UPLOAD_FOLDER/<path>')
def get_files(path):
    return send_from_directory(filemanager.upload_folder or app.config['UPLOAD_FOLDER'], path=path)

# create user
import base64


def create_user(app):
    """
        Create user with avatar from base64 encoded image
    """
    with app.app_context() as app:
        with open('tests/test.jpg', 'rb') as file:
            base64_image = str(base64.b64encode(file.read()), encoding='utf-8')
        user = User(
            email='email@gmail.com',
            username='username',
            avatar=base64_image,
        )
        db.session.add(user)
        db.session.commit()

create_user(app)
```
## User model 
<table><tr><th>id</th><th>email</th><th>username</th><th>avatar</th><tr><tr><td>1</td><td>email@gmail.com</td><td>username</td><td>UPLOAD_FOLDER&#x2F;images&#x2F;users&#x2F;avatars&#x2F;username.jpg</td></tr></table>

## Attention!
```python 
# DONT use this statement to update attached model's instance
db.session.query(Model).filter("condition").update(data)
# It doesn't trigger file attacher
# you can use this instead
for key, value in data.items():
    setattr(instance, key, value)
```

import base64
from tests.app import app, db, User

def create_user(app):
    with app.app_context() as app:
        with open('tests/test.jpg', 'rb') as file:
            base64_image = str(base64.b64encode(file.read()), encoding='utf-8')
        user = User(
            email='email@gmail.com',
            username='username',
            avatar=base64_image,
        ) 
        print(user.avatar) # path to file
        db.session.add(user)
        db.session.commit()

create_user(app)

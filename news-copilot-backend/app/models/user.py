from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    display_name = db.Column(db.String(120))
    avatar = db.Column(db.String(120))
    password = db.Column(db.String(128))

    def __init__(self, email, display_name=None, avatar=None, password=None):
        self.email = email
        self.display_name = display_name
        self.avatar = avatar
        self.password = password

    def __repr__(self):
        return "<User {}>".format(self.email)

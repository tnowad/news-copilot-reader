from flask_mail import Message
from app.extensions import mail


def send_reset_email(email, code):
    msg = Message("Password Reset Code", recipients=[email])
    msg.body = f"Your password reset code is: {code}"
    mail.send(msg)

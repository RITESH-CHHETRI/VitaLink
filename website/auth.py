from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

auth = Blueprint('auth', __name__)

baselink="127.0.0.1:5000"+"/otpverify"

def otpgenerator(name,mailid):
    unique=False
    while unique != True:
        unique=True
        otp = str(uuid4())
        gen=otp[:4]
        user = User.query.filter_by(otp=gen).first()
        if user:
            unique=False
        else:
            break

    msg = Message('VitaLink OTP VERIFICATION', sender =("VitaLink",'roguealex444@gmail.com'), recipients = [mailid])
    msg.body = f"OTP Verification for {name}\nYour otp is{gen}\nVerify it here:{baselink}\nThank you for using VitaLink\nPlease do not respond if you have not requested this email"
    mail.send(msg)
    return gen

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                if user.otp != "none":
                    return render_template("login-register.html", error = "Please verify your email first")
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                user.logined="true"
                db.session.commit()
                return redirect(url_for('views.home'))
            else:
                return render_template("login-register.html", error = "Wrong password")
        else:
            return render_template("login-register.html", error = "No user found")

    return render_template("login-register.html")


@auth.route('/logout')
@login_required
def logout():
    user=User.query.filter_by(id=current_user.id).first()
    user.logined="false"
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        profile = request.files['profile']
        status = request.form.get('status')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        pic=status+'.png'

        if user:
            return render_template("login-register.html", error = "Email already exists")
        elif len(email) < 6:
            return render_template("login-register.html", error = "Email must be greater than 6 characters")
        elif len(name) < 2:
            return render_template("login-register.html", error = "Name must be greater than 1 character")
        elif password1 != password2:
            return render_template("login-register.html", error = "passwords don't match")
        elif len(password1) < 7:
            return render_template("login-register.html", error = "Passwords must be greater than 7 character")
        else:
            if profile:
                if profile.content_type not in ['image/jpeg', 'image/png']:
                    return render_template("login-register.html", error = "Image should be in png or jpeg format")
                # check file size
                if profile.content_length > 10000:
                    return render_template("login-register.html", error = "Image file should be under 10 MB")
                pic=secure_filename(profile.filename)
                profile.save('website/static/profile/'+pic)

            new_user = User(email=email, name=name, password=generate_password_hash(
                password1, method='sha256'),websocket_id=uuid4().hex,profilepic=pic,status=status,otp=otpgenerator(name,email))
            db.session.add(new_user)
            db.session.commit()
            return redirect('/otpverify')

    return render_template("login-register.html")

@auth.route('/otpverify', methods=['GET', 'POST'])
def otpverify():
    if request.method == 'POST':
        otp=request.form.get('otp')
        user = User.query.filter_by(otp=otp).first()
        if user:
            user.otp="none"
            db.session.commit()
            return "<h1>Success</h1>"
        else:
            return "<h1>Failure</h1>"
    return render_template("test.html")

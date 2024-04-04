from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_moment import Moment
from flask_mail import Mail

db = SQLAlchemy()
DB_NAME = "database.db"
socketio = SocketIO()


def create_app():
    global mail
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'katsuren'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config['SECRET_KEY']='aisatpayslipgenerator'
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'email@gmail.com'
    app.config['MAIL_PASSWORD'] = 'mailpassword'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    db.init_app(app)
    #socketio.init_app(app)
    moment = Moment(app)
    mail = Mail(app)
    from .views import views
    from .auth import auth
    from .chat import chat
    from .diag import diag

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(chat, url_prefix='/')
    app.register_blueprint(diag, url_prefix='/')
    from .models import User, Post

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return socketio,app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

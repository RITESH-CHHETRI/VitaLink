from flask import Blueprint, render_template, request, flash, abort, current_app, redirect,url_for,jsonify
from flask_login import login_required, current_user
from .models import User, Message
from . import db
from sqlalchemy import exists, case
import random, string
from datetime import datetime
from . import socketio
import pusher
from datetime import datetime


app_id = "app id"
key = "key"
secret = "secret"
cluster = "mt1"

pusher = pusher_client = pusher.Pusher(
  app_id=app_id,
  key=key,
  secret=secret,
  cluster=cluster,
  ssl=True
)

chat = Blueprint('chat', __name__)


def uidgenerator(reciever,sender):
    uid = [reciever,sender]
    uid  = sorted(uid)
    return uid[0]+uid[1]

@chat.route('/chat',methods=['GET','POST'])
@login_required
def sessions():
    followingid = current_user.following.split("+")
    following = []
    messages=Message.query.all()
    for msg in messages:
        if (current_user.name in msg.uid) and msg.read=='false':
            msg.read='true'
    db.session.commit()
    for userid in followingid:
        user = User.query.filter_by(id=userid).first()
        following.append(user)
    if request.method == 'POST':
        reciever = request.form.get('chat')
        uid = uidgenerator(current_user.name,reciever)
        messages = Message.query.filter_by(uid=uid)
        count=messages.count()
        if messages == None:
            messages=[]
        reciever = User.query.filter_by(name=reciever).first()
        for message in messages:
            if message.sender == reciever.name:
                message.read = 'true'
        
        return render_template("chat.html",user=current_user,following = following,messages=messages,reciever=reciever,showchat=True,uid=uid,count=count)
    return render_template("chat.html",user=current_user,following = following,showchat=False,reciever=current_user)



@chat.route('/message', methods=['POST'])
def message():
    try:
        data = request.json
        message = data['message']
        user_id = data['user_id']
        pusher.trigger('private-user_' + user_id, 'new_message', {'sender':current_user.name,'message': message})
        now = datetime.now()
        day = now.strftime("%d-%m- %I:%M,%p")
        save_message = Message(uid=user_id,message=message,sender=current_user.name,posted=day)
        db.session.add(save_message)
        db.session.commit()
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'failure'})

@chat.route('/pusher/auth', methods=['POST'])
def pusher_authentication():
    auth = pusher.authenticate(channel=request.form['channel_name'], socket_id=request.form['socket_id'], custom_data={'user_id': request.headers.get('user_id')})
    return jsonify(auth)

@chat.route('/delmsg', methods=['POST'])
def delmsg():
    msg=request.form.get('msgdel')
    message = Message.query.filter_by(id=msg).first()
    db.session.delete(message)
    db.session.commit()
    return redirect("/chat")




import uuid
import twilio.jwt.access_token
import twilio.jwt.access_token.grants
import twilio.rest

twilio_client = twilio.rest.Client(twilio_key, twilio_secret, twilio_sid)

def find_or_create_room(room_name):
    try:
        twilio_client.video.rooms(room_name).fetch()
    except twilio.base.exceptions.TwilioRestException:
        twilio_client.video.rooms.create(unique_name=room_name, type="go")


def get_access_token(room_name):
    access_token = twilio.jwt.access_token.AccessToken(
        twilio_sid, twilio_key, twilio_secret, identity=uuid.uuid4().int
    )
    video_grant = twilio.jwt.access_token.grants.VideoGrant(room=room_name)
    access_token.add_grant(video_grant)
    return access_token


@chat.route("/join-room", methods=["POST"])
def join_room():
    reciever = request.form.get("video")
    sender = current_user.name 
    room_name=uidgenerator(reciever,sender)
    find_or_create_room(room_name)
    access_token = get_access_token(room_name)
    token = access_token.to_jwt()
    return render_template("video.html",room_name=room_name,token=token)
